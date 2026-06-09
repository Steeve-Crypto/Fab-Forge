import torch
import numpy as np
from typing import List
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback
import os

class FabEnv(gym.Env):
    """Gym-compatible environment for fab scheduling optimization - Terafab scale"""
    def __init__(self, num_wafers: int = 20, num_equipment: int = 5):
        super().__init__()
        self.num_wafers = num_wafers
        self.num_equipment = num_equipment
        self.observation_space = gym.spaces.Box(low=0, high=1000, shape=(num_wafers * num_equipment,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(num_equipment)  # Assign to one equipment

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.random.uniform(10, 200, (self.num_wafers, self.num_equipment)).astype(np.float32)  # processing times
        self.current_step = 0
        return self.state.flatten(), {}

    def step(self, action: int):
        # Simulate assignment and progression
        reward = -np.mean(self.state) * 0.1 - (action % 3)  # proxy for throughput + load balance
        self.state = np.roll(self.state, 1, axis=0)
        self.state *= 0.95  # simulate processing progress
        self.current_step += 1
        done = self.current_step >= 50  # episode length
        truncated = False
        info = {"throughput": -reward}
        return self.state.flatten(), reward, done, truncated, info

class RLFabOptimizer:
    """PPO-enhanced Reinforcement Learning Optimizer for FabForge - Terafab scale scheduling"""
    def __init__(self, num_wafers=20, num_equipment=5, model_path="models/ppo_fabforge.zip"):
        self.num_wafers = num_wafers
        self.num_equipment = num_equipment
        self.model_path = model_path
        self.env = make_vec_env(lambda: FabEnv(num_wafers, num_equipment), n_envs=4)
        self.model = None

    def train(self, total_timesteps: int = 100000):
        """Train PPO agent for fab scheduling optimization"""
        print("🚀 Training PPO Agent for Semiconductor Scheduling (Stable-Baselines3)...")
        print("This demonstrates advanced RL for Terafab throughput & yield optimization.")

        self.model = PPO("MlpPolicy", self.env, verbose=1, learning_rate=3e-4, n_steps=2048,
                         batch_size=64, gae_lambda=0.95, gamma=0.99, tensorboard_log="./tb_logs/")

        eval_env = make_vec_env(lambda: FabEnv(self.num_wafers, self.num_equipment), n_envs=1)
        eval_callback = EvalCallback(eval_env, best_model_save_path="./models/",
                                     log_path="./logs/", eval_freq=5000,
                                     deterministic=True, render=False)

        self.model.learn(total_timesteps=total_timesteps, callback=eval_callback)
        self.model.save(self.model_path)
        print("✅ PPO Training Complete! Model saved. Ready for Terafab production scheduling.")
        return self.model

    def optimize_schedule(self, current_state: np.ndarray) -> List[int]:
        """Generate optimized equipment assignment using trained PPO"""
        if self.model is None:
            try:
                self.model = PPO.load(self.model_path)
            except:
                print("No model found. Training a quick one...")
                self.train(total_timesteps=20000)

        # Reshape for single env prediction
        obs = current_state.reshape(1, -1).astype(np.float32)
        action, _ = self.model.predict(obs, deterministic=True)
        # Map to full schedule (demo: broadcast action)
        return [int(action[0])] * self.num_wafers

    def load(self):
        """Load pre-trained model"""
        if os.path.exists(self.model_path):
            self.model = PPO.load(self.model_path)
            print("✅ Loaded pre-trained PPO model for fab optimization.")

if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    optimizer = RLFabOptimizer()
    optimizer.train(total_timesteps=50000)  # Reduced for demo speed
