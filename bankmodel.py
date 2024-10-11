import simpy
import random
import matplotlib.pyplot as plt

# Parameters
RANDOM_SEED = 42
NEW_CUSTOMER_INTERVAL = 5  # Average time between customer arrivals
SERVICE_TIME = 3  # Average time it takes to serve a customer
SIM_TIME = 60  # Total simulation time

# Data tracking
queue_lengths = []
wait_times = []
server_utilization = []
busy_tellers = 0
total_customers_served = 0
total_wait_time = 0

# Customer arrival process
def customer(env, name, bank, arrival_time):
    global busy_tellers, total_customers_served, total_wait_time
    
    arrival_time = env.now
    print(f"{name} arrives at the bank at {arrival_time:.2f}.")
    
    with bank.tellers.request() as request:
        queue_length = len(bank.tellers.queue)
        queue_lengths.append(queue_length)  # Track queue length
        yield request
        
        wait_time = env.now - arrival_time
        wait_times.append(wait_time)  # Track wait time
        total_wait_time += wait_time
        
        print(f"{name} starts service at {env.now:.2f} (Waited {wait_time:.2f}).")
        busy_tellers += 1
        yield env.timeout(random.expovariate(1.0 / SERVICE_TIME))  # Service duration
        busy_tellers -= 1
        total_customers_served += 1
        
        print(f"{name} finishes service at {env.now:.2f}.")

# Generate customers at random intervals
def customer_generator(env, bank):
    i = 0
    while True:
        i += 1
        yield env.timeout(random.expovariate(1.0 / NEW_CUSTOMER_INTERVAL))  # Customer inter-arrival time
        env.process(customer(env, f'Customer {i}', bank, env.now))

# Define bank with tellers
class Bank:
    def __init__(self, env, num_tellers):
        self.env = env
        self.tellers = simpy.Resource(env, num_tellers)

# Main simulation setup
random.seed(RANDOM_SEED)
env = simpy.Environment()
bank = Bank(env, num_tellers=2)  # Number of tellers
env.process(customer_generator(env, bank))
env.run(until=SIM_TIME)

# Calculate average metrics
average_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
average_queue_length = sum(queue_lengths) / len(queue_lengths) if queue_lengths else 0
server_utilization_rate = (sum(queue_lengths) / (len(queue_lengths) * 2))  # Multiply by 2 tellers

print(f"\nAverage wait time: {average_wait_time:.2f} time units.")
print(f"Average queue length: {average_queue_length:.2f}.")
print(f"Server utilization: {server_utilization_rate:.2f}.")

# Plotting the results
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 10))

# Plot average queue length over time
ax1.plot(queue_lengths, label='Queue Length')
ax1.set_title('Queue Length Over Time')
ax1.set_xlabel('Event')
ax1.set_ylabel('Queue Length')
ax1.legend()

# Plot average wait time over time
ax2.plot(wait_times, label='Wait Times')
ax2.set_title('Wait Times Over Time')
ax2.set_xlabel('Event')
ax2.set_ylabel('Wait Time (time units)')
ax2.legend()

# Plot server utilization over time
server_utilization = [busy_tellers / 2.0 for _ in range(SIM_TIME)]  # Assuming 2 tellers
ax3.plot(server_utilization, label='Server Utilization')
ax3.set_title('Server Utilization Over Time')
ax3.set_xlabel('Time')
ax3.set_ylabel('Utilization')
ax3.legend()

plt.tight_layout()
plt.show()
