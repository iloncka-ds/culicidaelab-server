import time
import argparse
import subprocess
import psutil
import numpy as np
from tabulate import tabulate
from typing import List, Dict, Any
import json
from pathlib import Path


def get_process_and_children(proc: psutil.Process) -> List[psutil.Process]:
    """
    Recursively finds all child processes of a given process.
    """
    try:
        return [proc] + proc.children(recursive=True)
    except psutil.NoSuchProcess:
        return []


# --- This is the new, robust monitoring function ---
def monitor_process(process: subprocess.Popen, duration_seconds: int, interval: float) -> List[Dict[str, Any]]:
    """
    Monitors a process and its children for a given duration, sampling
    at a specified interval. This version is robust against process restarts.
    """
    metrics_log = []
    start_time = time.time()

    try:
        root_process = psutil.Process(process.pid)
    except psutil.NoSuchProcess:
        print(f"Error: Could not find process with PID {process.pid}.")
        return []

    print(
        f"Monitoring process '{root_process.name()}' (PID: {root_process.pid}) and its children for {duration_seconds} seconds..."
    )

    while time.time() - start_time < duration_seconds:
        # Step 1: Get the current list of processes and prime them.
        all_processes = get_process_and_children(root_process)
        for p in all_processes:
            try:
                p.cpu_percent()
            except psutil.Error:
                pass

        # Step 2: Wait for the specified interval.
        time.sleep(interval)

        # Step 3: Get the list of processes again and measure usage.
        total_cpu_percent = 0.0
        total_rss_bytes = 0
        all_processes = get_process_and_children(root_process)

        if not all_processes:
            print("The main server process appears to have terminated unexpectedly.")
            break

        for p in all_processes:
            try:
                total_cpu_percent += p.cpu_percent()
                total_rss_bytes += p.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        metrics_log.append(
            {
                "timestamp": time.time(),
                "cpu_percent": total_cpu_percent,
                "memory_rss_mb": total_rss_bytes / (1024 * 1024),
            }
        )

    return metrics_log


def analyze_results(metrics: List[Dict[str, Any]], command: str) -> Dict[str, Any]:
    """
    Analyzes the collected metrics, prints a summary table, and returns the summary.
    """
    if not metrics:
        print("No metrics were collected. Cannot generate a summary.")
        return {}

    # Skip the first measurement as it can be unreliable
    if len(metrics) > 1:
        metrics = metrics[1:]

    cpu_percentages = [m["cpu_percent"] for m in metrics]
    memory_usages_mb = [m["memory_rss_mb"] for m in metrics]

    summary = {
        "test_command": command,
        "monitoring_duration_sec": args.duration,
        "sampling_interval_sec": args.interval,
        "avg_cpu_usage_percent": float(np.mean(cpu_percentages)),
        "peak_cpu_usage_percent": float(np.max(cpu_percentages)),
        "avg_memory_rss_mb": float(np.mean(memory_usages_mb)),
        "peak_memory_rss_mb": float(np.max(memory_usages_mb)),
    }

    headers = ["Metric", "Value"]
    table = [
        ["Test Command", f"`{summary['test_command']}`"],
        ["Monitoring Duration", f"{summary['monitoring_duration_sec']} seconds"],
        ["Sampling Interval", f"{summary['sampling_interval_sec']} seconds"],
        ["-" * 20, "-" * 20],
        ["Average CPU Usage", f"{summary['avg_cpu_usage_percent']:.2f} %"],
        ["Peak CPU Usage", f"{summary['peak_cpu_usage_percent']:.2f} %"],
        ["-" * 20, "-" * 20],
        ["Average Memory (RSS)", f"{summary['avg_memory_rss_mb']:.2f} MB"],
        ["Peak Memory (RSS)", f"{summary['peak_memory_rss_mb']:.2f} MB"],
    ]

    print("\n--- Solara Web App Performance Summary ---")
    print(tabulate(table, headers=headers, tablefmt="grid"))
    return summary


def save_results_to_json(summary_data: dict, raw_metrics: list, output_file: str):
    """Saves the summary and raw metrics data to a JSON file."""
    if not summary_data:
        print("No summary data to save.")
        return

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    full_report = {"summary": summary_data, "raw_timeseries_data": raw_metrics}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=4)

    print(f"\nFull performance report saved to: {output_path}")


def main(args):
    """Main function to run the performance test."""
    solara_command = ["solara", "run", args.script_path, f"--port={args.port}"]
    command_str = " ".join(solara_command)

    print(f"Starting Solara application: `{command_str}`")

    process = subprocess.Popen(solara_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print(f"Waiting {args.init_wait} seconds for application to initialize...")
    time.sleep(args.init_wait)

    metrics_data = monitor_process(process, args.duration, args.interval)

    print("Monitoring finished. Terminating Solara application...")
    try:
        parent = psutil.Process(process.pid)
        for child in parent.children(recursive=True):
            child.terminate()
        parent.terminate()
        process.wait(timeout=10)
        print("Application terminated.")
    except psutil.NoSuchProcess:
        print("Process already terminated.")
    except subprocess.TimeoutExpired:
        print("Process did not terminate gracefully, forcing shutdown.")
        parent.kill()

    summary_data = analyze_results(metrics_data, command_str)

    if args.output_file:
        save_results_to_json(summary_data, metrics_data, args.output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Performance Tester for Solara Web Applications")
    parser.add_argument("script_path", type=str, help="Path to the Solara app (e.g., frontend.main)")
    parser.add_argument("--port", type=int, default=8765, help="Port to run the server on.")
    parser.add_argument(
        "--duration", type=int, default=30, help="Total duration to monitor the application in seconds."
    )
    parser.add_argument(
        "--interval", type=float, default=1.0, help="Interval between resource measurements in seconds."
    )
    parser.add_argument(
        "--init-wait", type=int, default=5, help="Time to wait for the Solara app to initialize before monitoring."
    )
    parser.add_argument(
        "--output-file", type=str, help="Path to save the results JSON file (e.g., reports/frontend_test.json)"
    )

    args = parser.parse_args()
    main(args)
