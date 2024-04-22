# import gymnasium as gym
# from gymnasium import spaces
import gym
import gym.spaces as spaces
import numpy as np
import pygame
import sys

class PongV2(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(PongV2, self).__init__()
        self.action_space = spaces.Discrete(4)  # Four actions: move left, right, up, down
        # self.observation_space = spaces.Box(low=0, high=1, shape=(6,), dtype=np.float32)
        # set self.observation_space to ba an array of 8 elements
        self.observation_space = spaces.Box(low=0, high=1, shape=(8,), dtype=np.float32)
        self.screen = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.puck_position = np.array([320, 240], dtype=np.float32)
        initial_velocity_x = np.random.choice([-3,2,-2,3,4,-4])
        initial_velocity_y = np.random.choice([-3,2,-2,3,4,-4])
        self.puck_velocity = np.array([initial_velocity_x, initial_velocity_y], dtype=np.float32)
        # self.puck_velocity = np.array([1, 3], dtype=np.float32)
        self.player_paddle_position = np.array([320, 460], dtype=np.float32)
        self.ai_paddle_position = np.array([320, 20], dtype=np.float32)
        self.score_player = 0
        self.score_ai = 0
        return self._get_obs()

    def step(self, action):
        self._handle_player_action(action)
        self._update_puck()
        self._ai_move()
        reward, done = self._check_goal()
        self._paddle_collision()
        return self._get_obs(), reward, done, {}

    def _get_obs(self):
        return np.concatenate([self.puck_position, self.puck_velocity, self.player_paddle_position, self.ai_paddle_position])

    def _handle_player_action(self, action):
        if action == 0 and self.player_paddle_position[0] > 0:  # Move left
            self.player_paddle_position[0] -= 5
        elif action == 1 and self.player_paddle_position[0] < 640:  # Move right
            self.player_paddle_position[0] += 5
        elif action == 2 and self.player_paddle_position[1] > 240:  # Move up
            self.player_paddle_position[1] -= 5
        elif action == 3 and self.player_paddle_position[1] < 480:  # Move down
            self.player_paddle_position[1] += 5

    def _update_puck(self):
        self.puck_position += self.puck_velocity
        # Bounce off walls
        if self.puck_position[0] <= 0 or self.puck_position[0] >= 640:
            self.puck_velocity[0] *= -1
        if self.puck_position[1] <= 0 or self.puck_position[1] >= 480:
            self.puck_velocity[1] *= -1

    def _paddle_collision(self):
        player_dist = np.linalg.norm(self.puck_position - self.player_paddle_position)
        ai_dist = np.linalg.norm(self.puck_position - self.ai_paddle_position)
        if player_dist < 50:
            self.puck_velocity[1] = -self.puck_velocity[1]
        if ai_dist < 30:
            self.puck_velocity[1] = -self.puck_velocity[1]

    # def _ai_move(self):
    #     self.ai_paddle_position[0] += np.random.randint(-3,3)
    #     if self.puck_position[0] > self.ai_paddle_position[0]+25:
    #         self.ai_paddle_position[0] += 3
    #     elif self.puck_position[0] < self.ai_paddle_position[0]-25:
    #         self.ai_paddle_position[0] -= 3
    def _ai_move(self):
    # Apply a random horizontal movement more strongly
        random_shift = np.random.randint(-10, 10)  # Wider range for more pronounced random movement
        self.ai_paddle_position[0] += random_shift
        
        # Conditional deterministic movement towards the puck with a relaxed condition
        if self.puck_position[0] > self.ai_paddle_position[0] + 30:  # Slightly increased buffer for movement
            self.ai_paddle_position[0] += 3  # Increase the step size for faster catching up
        elif self.puck_position[0] < self.ai_paddle_position[0] - 30:
            self.ai_paddle_position[0] -= 3

    # Ensure AI paddle doesn't move out of bounds
        self.ai_paddle_position[0] = np.clip(self.ai_paddle_position[0], 0, 640)

    def _check_goal(self):
        if self.puck_position[1] >= 480:
            self.score_ai += 1
            return -10000, True
        elif self.puck_position[1] <= 0:
            self.score_player += 1
            return 10000, True
        return 0, False

    def render(self, mode='human'):
        self.screen.fill((0, 0, 0))
        pygame.draw.circle(self.screen, (255, 0, 0), self.puck_position.astype(int), 15)
        pygame.draw.rect(self.screen, (0, 0, 255), (*self.player_paddle_position, 60, 10))
        pygame.draw.rect(self.screen, (255, 255, 255), (*self.ai_paddle_position, 60, 10))
        pygame.display.flip()
        self.clock.tick(1000)


    def close(self):
        pygame.quit()
        sys.exit()

# Test Usage
# env = AirHockeyEnv()
# done = False
# while not done:
#     env.render()
#     action = env.action_space.sample()
#     # print(action)

#     obs, reward, done, info = env.step(action)
#     # print("Observation:")
#     # print(obs)
#     # print("Reward:")
#     # print(reward)
#     if reward == 1:
#         print("Agent scored!")
# env.close()