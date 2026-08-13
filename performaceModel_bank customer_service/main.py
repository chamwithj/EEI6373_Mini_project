"""Bank Customer Service Performance Analysis using Queueing Theory."""
import math
import matplotlib.pyplot as plt

ARRIVAL_DATA = [
    ("9:00-9:30", 18), ("9:30-10:00", 22), ("10:00-10:30", 26),
    ("10:30-11:00", 31), ("11:00-11:30", 24), ("11:30-12:00", 19),
    ("12:00-12:30", 35), ("12:30-13:00", 32), ("13:00-13:30", 27),
    ("13:30-14:00", 18), ("14:00-14:30", 13), ("14:30-15:00", 14),
    ("15:00-15:30", 24), ("15:30-16:00", 34), ("16:00-16:30", 25),
    ("16:30-17:00", 22),
]
OBSERVATION_HOURS = 8
SERVICE_RATE = 60
WAITING_TIME_TARGET = 5


def calculate_mm1(arrival_rate, service_rate):
    """Return M/M/1 performance metrics; rates are customers/hour."""
    rho = arrival_rate / service_rate
    if rho >= 1:
        return {"stable": False, "rho": rho, "Lq": math.inf,
                "L": math.inf, "Wq_min": math.inf, "W_min": math.inf}
    Lq = arrival_rate**2 / (service_rate * (service_rate - arrival_rate))
    L = arrival_rate / (service_rate - arrival_rate)
    Wq = arrival_rate / (service_rate * (service_rate - arrival_rate))
    W = 1 / (service_rate - arrival_rate)
    return {"stable": True, "rho": rho, "Lq": Lq, "L": L,
            "Wq_min": Wq * 60, "W_min": W * 60}


def calculate_mmc(arrival_rate, service_rate_per_server, servers):
    """Return M/M/c average waiting time and utilization."""
    lam = arrival_rate / 60.0
    mu = service_rate_per_server / 60.0
    rho = lam / (servers * mu)
    if rho >= 1:
        return {"stable": False, "rho": rho, "wait_min": math.inf}
    a = lam / mu
    p0_den = sum((a**k) / math.factorial(k) for k in range(servers))
    last = (a**servers) / (math.factorial(servers) * (1 - rho))
    p0 = 1 / (p0_den + last)
    pw = last * p0
    wq_minutes = (pw / ((servers * mu) - lam)) * 60
    return {"stable": True, "rho": rho, "wait_min": wq_minutes}


def main():
    total_customers = sum(n for _, n in ARRIVAL_DATA)
    avg_lambda = total_customers / OBSERVATION_HOURS
    result = calculate_mm1(avg_lambda, SERVICE_RATE)

    print("=" * 65)
    print("BANK CUSTOMER SERVICE PERFORMANCE ANALYSIS")
    print("=" * 65)
    print("\nSimulated Customer Arrival Data")
    print(f"{'Time Period':<18}{'Customers':<15}{'Hourly Equivalent':<20}")
    for period, customers in ARRIVAL_DATA:
        print(f"{period:<18}{customers:<15}{customers * 2:<20}")
    print("-" * 65)
    print(f"Total customers: {total_customers}")
    print(f"Observation period: {OBSERVATION_HOURS} hours")
    print(f"Average arrival rate (lambda): {avg_lambda:.2f} customers/hour")
    print(f"Assumed service rate (mu): {SERVICE_RATE:.2f} customers/hour")

    print("\nM/M/1 QUEUEING MODEL RESULTS")
    print(f"Traffic intensity (rho): {result['rho']:.3f}")
    print(f"Server utilization: {result['rho'] * 100:.1f}%")
    print(f"Average number in queue (Lq): {result['Lq']:.2f} customers")
    print(f"Average number in system (L): {result['L']:.2f} customers")
    print(f"Average waiting time (Wq): {result['Wq_min']:.2f} minutes")
    print(f"Average time in system (W): {result['W_min']:.2f} minutes")

    # Arrival-rate sensitivity: how waiting changes as demand approaches capacity.
    arrival_rates = [30, 36, 42, 48, 51, 54, 57, 59]
    waiting_times = [calculate_mm1(x, SERVICE_RATE)["Wq_min"] for x in arrival_rates]
    print("\nARRIVAL-RATE SENSITIVITY")
    for x, w in zip(arrival_rates, waiting_times):
        print(f"{x:>3} customers/hour -> {w:.2f} minutes waiting")

    # Peak and low periods.
    peak_period, peak_n = max(ARRIVAL_DATA, key=lambda x: x[1])
    low_period, low_n = min(ARRIVAL_DATA, key=lambda x: x[1])
    print(f"\nPeak period: {peak_period} ({peak_n} customers / 30 min = {peak_n*2}/hour equivalent)")
    print(f"Lowest period: {low_period} ({low_n} customers / 30 min = {low_n*2}/hour equivalent)")

    # M/M/c staffing sensitivity using the same 60 customers/hour capacity per officer.
    print("\nSTAFFING SENSITIVITY (M/M/c)")
    staffing = []
    for officers in [1, 2, 3]:
        r = calculate_mmc(avg_lambda, SERVICE_RATE, officers)
        wait = r["wait_min"]
        print(f"{officers} officer(s): utilization={r['rho']*100:.1f}%, waiting={wait:.2f} min")
        staffing.append((officers, wait))

    periods = [x[0] for x in ARRIVAL_DATA]
    hourly_rates = [x[1] * 2 for x in ARRIVAL_DATA]

    # Figure 1: arrival rate by time.
    plt.figure(figsize=(11, 5))
    plt.bar(periods, hourly_rates)
    plt.axhline(SERVICE_RATE, linestyle="--", label="Service capacity = 60/hour")
    plt.xlabel("Time Period")
    plt.ylabel("Arrival Rate (customers/hour)")
    plt.title("Customer Arrival Rate by Time Period")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig("figure1_customer_arrival_rate.png", dpi=300)
    plt.show()

    # Figure 2: waiting time versus arrival rate.
    plt.figure(figsize=(9, 5))
    plt.plot(arrival_rates, waiting_times, marker="o")
    plt.xlabel("Arrival Rate (customers/hour)")
    plt.ylabel("Average Waiting Time (minutes)")
    plt.title("Average Waiting Time versus Arrival Rate")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("figure2_waiting_time_vs_arrival_rate.png", dpi=300)
    plt.show()

    # Figure 3: utilization.
    busy = result["rho"] * 100
    idle = 100 - busy
    plt.figure(figsize=(6, 6))
    plt.pie([busy, idle], labels=[f"Busy ({busy:.1f}%)", f"Idle ({idle:.1f}%)"],
            autopct="%1.1f%%", startangle=90)
    plt.title("Customer Service Officer Utilization")
    plt.tight_layout()
    plt.savefig("figure3_server_utilization.png", dpi=300)
    plt.show()

    # Figure 4: staffing comparison.
    plt.figure(figsize=(8, 5))
    plt.bar([str(x[0]) for x in staffing], [x[1] for x in staffing])
    plt.axhline(WAITING_TIME_TARGET, linestyle="--",
                label=f"Waiting-time target = {WAITING_TIME_TARGET} min")
    plt.xlabel("Number of Service Officers")
    plt.ylabel("Average Waiting Time (minutes)")
    plt.title("Effect of Additional Service Officers on Waiting Time")
    plt.legend()
    plt.tight_layout()
    plt.savefig("figure4_staffing_comparison.png", dpi=300)
    plt.show()

    print("\nAnalysis complete. Four figures were saved as PNG files.")


if __name__ == "__main__":
    main()
