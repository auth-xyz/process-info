import psutil
import GPUtil
import time
import argparse

from rich.table import Table
from rich.live import Live


def get_process_stats(process):
    cpu_percent = process.cpu_percent(interval=1)
    memory_info = process.memory_info()
    memory_usage = memory_info.rss / (1024 * 1024)  # Convert to MB

    gpu_usage = None
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_usage = gpus[0].load * 100
    except Exception as e:
        print("Error while checking GPU usage:", str(e))

    return cpu_percent, memory_usage, gpu_usage


def main():
    parser = argparse.ArgumentParser(description="Monitor process statistics.")
    parser.add_argument("processes", type=str, help="List of process names separated by comma")
    parser.add_argument("--watch", type=str, help="Watch mode for a specified duration (e.g., 60s)")
    args = parser.parse_args()

    process_names = args.processes.split(',')
    watch_duration = None

    if args.watch:
        watch_duration = args.watch
        if watch_duration[-1] == "s":
            watch_duration = int(watch_duration[:-1])

    processes = [psutil.Process() for _ in range(len(process_names))]
    table = Table(show_header=True, header_style="bold")
    table.add_column("Process Name")
    table.add_column("CPU Usage (%)")
    table.add_column("Memory Usage (MB)")
    table.add_column("GPU Usage (%)")

    def update_table():
        new_table = Table(show_header=True, header_style="bold")
        new_table.add_column("Process Name")
        new_table.add_column("CPU Usage (%)")
        new_table.add_column("Memory Usage (MB)")
        new_table.add_column("GPU Usage (%)")

        for i, process in enumerate(processes):
            cpu_percent, memory_usage, gpu_usage = get_process_stats(process)
            new_table.add_row(
                process_names[i],
                f"{cpu_percent:.2f}",
                f"{memory_usage:.2f}",
                f"{gpu_usage:.2f}" if gpu_usage is not None else "N/A"
            )

        return new_table

    with Live(table, refresh_per_second=4) as live:
        start_time = time.time()

        while True:
            if watch_duration is not None and time.time() - start_time > watch_duration:
                break

            table = update_table()  # Replace the existing table with the updated one
            table.title = "Process Monitor (Press Ctrl+C to exit)"
            live.update(table)
            time.sleep(1)


if __name__ == "__main__":
    main()
