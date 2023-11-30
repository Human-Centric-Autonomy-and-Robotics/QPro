from envs.multiagentenv import MultiAgentEnv
from utils.dict2namedtuple import convert
import numpy as np
import torch as th

# this non-monotonic matrix can be solved by qmix
payoff_values2 = [[8, 0, 0],
                  [0, 0, 0],
                  [0, 0, 0]]

payoff_values = [[0, 0, 0],
                 [0, 0, 0],
                 [8, 0, 0]]

# payoff_values2 = [[8, -6.1, -6.1],
#                   [-6.1, 0, 0],
#                   [0, -6.1, -6.1]]
#
# payoff_values = [[0, -6.1, -6.1],
#                  [-6.1, 0, 0],
#                  [8, -6.1, -6.1]]

# payoff_values2 = [[8, -12.1, -12.1],
#                   [-12.1, 0, 0],
#                   [-12.1, 0, 0]]
#
# payoff_values = [[-12.1, -12.1, -12.1],
#                  [-12.1, 0, 0],
#                  [8, 0, 0]]


# payoff_values2 = [[0, 0, -12.1],
#                     [0, 0, -12.1],
#                     [-12.1, -12.1, 8]]
#
# payoff_values = [[8, -12.1, -12.1],
#                     [-12.1, 0, 0],
#                     [-12.1, 0, 0]]

# payoff_values = [[12, -0.1, -0.1],
#                     [-0.1, 0, 0],
#                     [-0.1, 0, 0]]

# payoff_values = [[12, -12, -12],
#                     [-12, 0, 0],
#                     [-12, 0, 0]]

# payoff_values = [[12, 0, 10],
#                     [0, 0, 10],
#                     [10, 10, 10]]


# payoff_values = [[1, 0], [0, 1]]
# n_agents = 3
# payoff_values = np.zeros((n_agents, n_agents))
# for i in range(n_agents):
#     payoff_values[i, i] = 1

class OneStepMatrixGame(MultiAgentEnv):
    def __init__(self, batch_size=None, **kwargs):
        # Define the agents
        self.n_agents = 2
        self.state_id = 0
        # Define the internal state
        self.steps = 0
        self.n_actions = len(payoff_values[0])
        self.episode_limit = 1

    def reset(self):
        """ Returns initial observations and states"""
        self.steps = 0
        return self.get_obs(), self.get_state()

    def step(self, actions):
        """ Returns reward, terminated, info """
        id = self.state_id
        if id == 0:
            reward = payoff_values[actions[0]][actions[1]]
        elif id == 1:
            reward = payoff_values2[actions[0]][actions[1]]
        else:
            reward = payoff_values[actions[0]][actions[1]]
        self.steps = 1
        self.state_id = np.random.randint(0, 2)
        terminated = True

        info = {}
        return reward, terminated, info

    def get_obs(self):
        """ Returns all agent observations in a list """
        """setting 1"""
        # one_hot_step = np.zeros(2)
        # one_hot_step[self.steps] = 1
        # return [np.copy(one_hot_step) for _ in range(self.n_agents)]

        """setting 2"""

        state_id = self.state_id
        obs11 = np.array([1, 1])
        obs12 = np.array([1, 2])
        obs22 = np.array([2, 2])
        s1obs = []
        s1obs.append(np.copy(obs11))
        s1obs.append(np.copy(obs12))
        s2obs = []
        s2obs.append(np.copy(obs11))
        s2obs.append(np.copy(obs22))
        if state_id == 0:
            return s1obs
        elif state_id == 1:
            return s2obs
        return s1obs
    def get_obs_agent(self, agent_id):
        """ Returns observation for agent_id """
        return self.get_obs()[agent_id]

    def get_obs_size(self):
        """ Returns the shape of the observation """
        return len(self.get_obs_agent(1))

    def get_state(self):
        return self.get_obs_agent(0)
#        return self.get_obs_agent(1)

    def get_state_size(self):
        """ Returns the shape of the state"""
        return self.get_obs_size()

    def get_avail_actions(self):
        avail_actions = []
        for agent_id in range(self.n_agents):
            avail_agent = self.get_avail_agent_actions(agent_id)
            avail_actions.append(avail_agent)
        return avail_actions

    def get_avail_agent_actions(self, agent_id):
        """ Returns the available actions for agent_id """
        return np.ones(self.n_actions)

    def get_total_actions(self):
        """ Returns the total number of actions an agent could ever take """
        return self.n_actions

    def get_stats(self):
        return None

    def render(self):
        raise NotImplementedError

    def close(self):
        pass

    def seed(self):
        raise NotImplementedError


# for mixer methods
def print_matrix_status(batch, mixer, mac_out):
    batch_size = batch.batch_size
    matrix_size = len(payoff_values)
    results = th.zeros((matrix_size, matrix_size))

    with th.no_grad():
        for i in range(results.shape[0]):
            for j in range(results.shape[1]):
                actions = th.LongTensor([[[[i], [j]]]]).to(device=mac_out.device).repeat(batch_size, 1, 1, 1)
                if len(mac_out.size()) == 5:  # n qvals
                    actions = actions.unsqueeze(-1).repeat(1, 1, 1, 1, mac_out.size(-1))  # b, t, a, actions, n
                qvals = th.gather(mac_out[:batch_size, 0:1], dim=3, index=actions).squeeze(3)

                global_q = mixer(qvals, batch["state"][:batch_size, 0:1]).mean()
                results[i][j] = global_q.item()

    th.set_printoptions(1, sci_mode=False)
    print(results)
    if len(mac_out.size()) == 5:
        mac_out = mac_out.mean(-1)
    print(mac_out.mean(dim=(0, 1)).detach().cpu())
    th.set_printoptions(4)


def print_one_matrix_status(batch, mixer, mac_out):
    batch_size = 1
    matrix_size = len(payoff_values)
    results = th.zeros((matrix_size, matrix_size))

    with th.no_grad():
        for i in range(results.shape[0]):
            for j in range(results.shape[1]):
                actions = th.LongTensor([[[[i], [j]]]]).to(device=mac_out.device).repeat(batch_size, 1, 1, 1)
                if len(mac_out.size()) == 5:  # n qvals
                    actions = actions.unsqueeze(-1).repeat(1, 1, 1, 1, mac_out.size(-1))  # b, t, a, actions, n
                qvals = th.gather(mac_out[:batch_size, 0:1], dim=3, index=actions).squeeze(3)
                #FOR OTHERS
                global_q = mixer(qvals, batch["state"][:batch_size, 0:1]).mean()
                #FOR QTRAN
                #global_q = mixer(qvals, batch["state"][:batch_size, 0:1]).mean()
                results[i][j] = global_q.item()

    th.set_printoptions(1, sci_mode=False)
    print(results)
    if len(mac_out.size()) == 5:
        mac_out = mac_out.mean(-1)
    print(mac_out.mean(dim=(0, 1)).detach().cpu())
    th.set_printoptions(4)

def print_certain_matrix_status(batch, mixer, mac_out, num = 0):
    print('obs: \n',batch.data.transition_data['obs'][num][0:1])
    print('action: \n', batch.data.transition_data['actions'][num][0:1])
    batch_size = 1
    matrix_size = len(payoff_values)
    results = th.zeros((matrix_size, matrix_size))

    with th.no_grad():
        for i in range(results.shape[0]):
            for j in range(results.shape[1]):
                actions = th.LongTensor([[[[i], [j]]]]).to(device=mac_out.device).repeat(batch_size, 1, 1, 1)
                if len(mac_out.size()) == 5:  # n qvals
                    actions = actions.unsqueeze(-1).repeat(1, 1, 1, 1, mac_out.size(-1))  # b, t, a, actions, n
                qvals = th.gather(mac_out[num : num+batch_size, 0:1], dim=3, index=actions).squeeze(3)

                global_q = mixer(qvals, batch["state"][num:num+batch_size, 0:1]).mean()
                results[i][j] = global_q.item()

    th.set_printoptions(1, sci_mode=False)
    print(results)
    if len(mac_out.size()) == 5:
        mac_out = mac_out.mean(-1)
    print(mac_out[num : num+batch_size, 0:1])
    th.set_printoptions(4)