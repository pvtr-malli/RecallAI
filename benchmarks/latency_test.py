#!/usr/bin/env python3
"""
Performance benchmarking script for RecallAI.

Measures latency metrics (min, max, p50, p90, p95) for both search and answer modes.
"""

import time
import statistics
import requests
from typing import Any
from dataclasses import dataclass


@dataclass
class LatencyStats:
    """
    Container for latency statistics.
    """

    min: float
    max: float
    p50: float
    p90: float
    p95: float
    mean: float
    total_runs: int


# Test questions covering various topics.
TEST_QUERIES = [
    "How to handle multi-morality features ",
    "what is tools in agents?",
    "what is mlops",

    "give the introduction to agents",
    "what is future stores",

    "why FM are recommended for ad-click prediction?",
    "foundational model paradigm - explain",
    "Explain idempotency in API design",

    "multi task calssifier implementation",
    "What is the time complexity of quicksort?", # its not there
    "agent simple start with langchan",

    "what is vertec ai",
    "extension in ai agents",
    "functions in ai agent use cases",

    # Database.
    "How to optimize SQL queries for performance?", # this is not there
    "What is database indexing and when to use it?", # this is not there
]


def measure_latency(
    query: str,
    mode: str,
    api_url: str = "http://localhost:8000/search",
    runs: int = 10,
    search_in: str = "both",
    top_k: int = 5,
    verbose: bool = False
) -> list[float]:
    """
    Measure latency for a single query across multiple runs.

    param query: Search query to test.
    param mode: Mode to test ("search" or "answer").
    param api_url: API endpoint URL.
    param runs: Number of times to run the query.
    param search_in: Where to search ("documents", "code", "both").
    param top_k: Number of results to retrieve.
    param verbose: If True, print response details.
    """
    latencies = []

    for i in range(runs):
        payload = {
            "query": query,
            "mode": mode,
            "search_in": search_in,
            "top_k": top_k
        }

        try:
            start_time = time.time()
            response = requests.post(api_url, json=payload, timeout=120)
            end_time = time.time()

            if response.status_code == 200:
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                print(f"  Run {i+1}/{runs}: {latency_ms:.2f}ms")

                # Print response details if verbose.
                if verbose:  # Only print first run to avoid clutter.
                    try:
                        result = response.json()
                        print(f"  └─ Response keys: {list(result.keys())}")

                        if mode == "search" and "results" in result:
                            print(f"  └─ Found {len(result.get('results', []))} results")
                            if result.get('results'):
                                first_result = result['results'][0]
                                print(f"  └─ Top result: {first_result.get('file_path', 'N/A')} "
                                      f"(score: {first_result.get('score', 0):.4f})")
                        elif mode == "answer" and "answer" in result:
                            answer_preview = result['answer'][:100].replace('\n', ' ')
                            print(f"  └─ Answer preview: {answer_preview}...")
                            print(f"  └─ Sources: {len(result.get('sources', []))} files")
                        else:
                            print(f"  └─ Response: {str(result)[:200]}")
                    except Exception as e:
                        print(f"  └─ Could not parse response: {str(e)}")
            else:
                print(f"  Run {i+1}/{runs}: Failed (HTTP {response.status_code})")
                print(f"  └─ Response: {response.text[:200]}")
        except requests.exceptions.Timeout:
            print(f"  Run {i+1}/{runs}: Timeout (>120s)")
        except Exception as e:
            print(f"  Run {i+1}/{runs}: Error - {str(e)}")

    return latencies


def calculate_stats(latencies: list[float]) -> LatencyStats:
    """
    Calculate statistical metrics from latency measurements.

    param latencies: List of latency measurements in milliseconds.
    """
    if not latencies:
        return LatencyStats(0, 0, 0, 0, 0, 0, 0)

    sorted_latencies = sorted(latencies)
    n = len(sorted_latencies)

    return LatencyStats(
        min=min(sorted_latencies),
        max=max(sorted_latencies),
        p50=statistics.median(sorted_latencies),
        p90=sorted_latencies[int(0.90 * n)] if n > 0 else 0,
        p95=sorted_latencies[int(0.95 * n)] if n > 0 else 0,
        mean=statistics.mean(sorted_latencies),
        total_runs=n
    )


def format_latency(ms: float) -> str:
    """
    Format latency value with appropriate units.

    param ms: Latency in milliseconds.
    """
    if ms < 1000:
        return f"{ms:.2f}ms"
    else:
        return f"{ms/1000:.2f}s"


def print_stats(mode: str, stats: LatencyStats) -> None:
    """
    Print latency statistics in a formatted table.

    param mode: Mode tested ("search" or "answer").
    param stats: Latency statistics.
    """
    print(f"\n{'='*60}")
    print(f"  {mode.upper()} MODE - Latency Statistics ({stats.total_runs} runs)")
    print(f"{'='*60}")
    print(f"  Min:    {format_latency(stats.min)}")
    print(f"  Max:    {format_latency(stats.max)}")
    print(f"  Mean:   {format_latency(stats.mean)}")
    print(f"  P50:    {format_latency(stats.p50)}")
    print(f"  P90:    {format_latency(stats.p90)}")
    print(f"  P95:    {format_latency(stats.p95)}")
    print(f"{'='*60}\n")


def run_benchmark(
    queries: list[str],
    mode: str,
    runs_per_query: int = 10,
    api_url: str = "http://localhost:8000/search",
    verbose: bool = True
) -> None:
    """
    Run benchmarks for a specific mode across all queries.

    param queries: List of test queries.
    param mode: Mode to test ("search" or "answer").
    param runs_per_query: Number of runs per query.
    param api_url: API endpoint URL.
    param verbose: If True, print response details for first run of each query.
    """
    print(f"\n{'#'*60}")
    print(f"  Starting {mode.upper()} mode benchmark")
    print(f"  Testing {len(queries)} queries x {runs_per_query} runs each")
    print(f"{'#'*60}\n")

    all_latencies = []

    for idx, query in enumerate(queries, 1):
        print(f"\n[{idx}/{len(queries)}] Query: {query[:60]}...")
        latencies = measure_latency(query, mode, api_url, runs_per_query, verbose=verbose)
        all_latencies.extend(latencies)

        if latencies:
            query_stats = calculate_stats(latencies)
            print(f"  → Query stats: min={format_latency(query_stats.min)}, "
                  f"p50={format_latency(query_stats.p50)}, "
                  f"max={format_latency(query_stats.max)}")

    # Calculate and print overall statistics.
    if all_latencies:
        overall_stats = calculate_stats(all_latencies)
        print_stats(mode, overall_stats)
    else:
        print(f"\n⚠️  No successful runs for {mode} mode\n")


def main() -> None:
    """
    Main entry point for the benchmark script.
    """
    print("\n" + "="*60)
    print("  RecallAI Performance Benchmark")
    print("="*60)
    print(f"  API URL: http://localhost:8000/search")
    print(f"  Test queries: {len(TEST_QUERIES)}")
    print(f"  Runs per query: 10 (search) / 3 (answer)")
    print("="*60)

    # Check if API is available.
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is reachable\n")
        else:
            print("⚠️  API returned unexpected status\n")
    except Exception as e:
        print(f"❌ Cannot reach API: {str(e)}")
        print("   Please ensure RecallAI is running (python recall_ai/app.py)\n")
        return

    # Run benchmarks for search mode (fast, many runs).
    run_benchmark(TEST_QUERIES, mode="search", runs_per_query=10)

    # Run benchmarks for answer mode (slow, fewer runs).
    print("\n⏳ Starting answer mode benchmark (this will take several minutes)...\n")
    run_benchmark(TEST_QUERIES, mode="answer", runs_per_query=3)

    print("\n" + "="*60)
    print("  Benchmark Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
