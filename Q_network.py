import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque

from game import Game  # must implement get_state() and play_step(action)

# --- Model ---
class DQN(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# --- Hyperparameters ---
learning_rate = 0.001
gamma = 0.99
epsilon = 1.0
epsilon_min = 0.01
epsilon_decay = 0.995
batch_size = 64
target_update_freq = 1000
memory_size = 10000
episodes = 1000

# --- Initialize Networks ---
input_dim = 11
hidden_dim = 256
output_dim = 3
policy_net = DQN(input_dim, hidden_dim, output_dim)
target_net = DQN(input_dim, hidden_dim, output_dim)
target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

optimizer = optim.Adam(policy_net.parameters(), lr=learning_rate)
memory = deque(maxlen=memory_size)

# --- Epsilon-greedy Action Selection ---
def select_action(state, epsilon):
    if random.random() < epsilon:
        return random.randint(0, 2)
    else:
        state_t = torch.FloatTensor(state).unsqueeze(0)
        q_values = policy_net(state_t)
        return torch.argmax(q_values).item()

# --- Optimize Model ---
def optimize_model():
    if len(memory) < batch_size:
        return
    
    batch = random.sample(memory, batch_size)
    state_batch, action_batch, reward_batch, next_state_batch, done_batch = zip(*batch)

    state_batch = torch.FloatTensor(state_batch)
    action_batch = torch.LongTensor(action_batch).unsqueeze(1)
    reward_batch = torch.FloatTensor(reward_batch)
    next_state_batch = torch.FloatTensor(next_state_batch)
    done_batch = torch.FloatTensor(done_batch)

    q_values = policy_net(state_batch).gather(1, action_batch).squeeze()

    with torch.no_grad():
        max_next_q_values = target_net(next_state_batch).max(1)[0]
        target_q_values = reward_batch + gamma * max_next_q_values * (1 - done_batch)

    loss = nn.MSELoss()(q_values, target_q_values)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

# --- Training Loop ---
def train():
    global epsilon
    rewards_per_episode = []
    steps_done = 0

    for episode in range(episodes):
        game = Game()
        state = game.get_state()   # must be defined in your Game class
        episode_reward = 0
        done = False

        while not done:
            action = select_action(state, epsilon)
            old_state = game.get_state()
            reward, done, score= game.play_step(action)
            next_state = game.get_state()
            memory.append((old_state, action, reward, next_state, done))
            state = next_state
            episode_reward += reward
            optimize_model()

            if steps_done % target_update_freq == 0:
                target_net.load_state_dict(policy_net.state_dict())

            steps_done += 1

        epsilon = max(epsilon_min, epsilon * epsilon_decay)
        rewards_per_episode.append(episode_reward)

        print(f"Episode {episode + 1}/{episodes}, Reward: {episode_reward}, Epsilon: {epsilon:.3f}")

    return rewards_per_episode

if __name__ == "__main__":
    train()
