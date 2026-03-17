"""Model definitions for SO-100 imitation policies."""

from __future__ import annotations

import abc
from typing import Literal, TypeAlias

import torch
from torch import nn


class BasePolicy(nn.Module, metaclass=abc.ABCMeta):
    """Base class for action chunking policies."""

    def __init__(self, state_dim: int, action_dim: int, chunk_size: int) -> None:
        super().__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.chunk_size = chunk_size

    @abc.abstractmethod
    def compute_loss(
        self, state: torch.Tensor, action_chunk: torch.Tensor
    ) -> torch.Tensor:
        """Compute training loss for a batch."""

    @abc.abstractmethod
    def sample_actions(
        self,
        state: torch.Tensor,
    ) -> torch.Tensor:
        """Generate a chunk of actions with shape (batch, chunk_size, action_dim)."""


# TODO: Students implement ObstaclePolicy here.
class ObstaclePolicy(BasePolicy):
    """Predicts action chunks with an MSE loss.

    A simple MLP that maps a state vector to a flat action chunk
    (chunk_size * action_dim) and reshapes to (B, chunk_size, action_dim).
    """

    def __init__(
        self,
        action_dim: int,
        state_dim: int,
        chunk_size: int,
        d_model: int,
        depth: int,
    ) -> None:
        super().__init__(state_dim, action_dim, chunk_size)
        layers = [nn.Linear(state_dim, d_model), nn.GELU()]
        for _ in range(depth-2):
            layers += [nn.Linear(d_model, d_model), nn.GELU()]
        layers += [nn.Linear(d_model, chunk_size*action_dim)]
        self.net = nn.Sequential(*layers)

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        """Return predicted action chunk of shape (B, chunk_size, action_dim)."""
        assert x.shape[1] == self.state_dim, f"x should have dim[1] = {self.state_dim} but has {x.size(1)} instead"
        out = self.net(x)
        return out.view(x.shape[0], self.chunk_size, self.action_dim)

    def compute_loss(
        self,
        predictions: torch.Tensor,
        actions: torch.Tensor
    ) -> torch.Tensor:
        assert predictions.shape == actions.shape, f"Predictions and actions should have the same shape, have shapes {predictions.shape} and {actions.shape} respectively instead"
        return torch.nn.functional.mse_loss(predictions, actions)

    @torch.no_grad()
    def sample_actions(
        self,
        state: torch.Tensor,
    ) -> torch.Tensor:
        assert state.shape[1] == self.state_dim, f"state should have dim[1] = {self.state_dim} but has {x.size(1)} instead"
        return self(state)

# TODO: Students implement MultiTaskPolicy here.
class MultiTaskPolicy(BasePolicy):
    """Goal-conditioned policy for the multicube scene."""

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        chunk_size: int,
        d_model: int,
    ) -> None:
        super().__init__(state_dim, action_dim, chunk_size)
        self.l1 = nn.Sequential(
                nn.Linear(state_dim, d_model),
                nn.GELU(),
                )
        self.gru = nn.GRU(d_model, d_model)
        self.l2 = nn.Linear(d_model, chunk_size*action_dim)

    def compute_loss(
        self,
        predictions: torch.Tensor,
        actions: torch.Tensor
    ) -> torch.Tensor:
        assert predictions.shape == actions.shape, f"Predictions and actions should have the same shape, have shapes {predictions.shape} and {actions.shape} respectively instead"
        loss_ee = nn.functional.mse_loss(predictions[:][:][:3], actions[:][:][:3])
        loss_gripper = nn.functional.mse_loss(predictions[:][:][-1], actions[:][:][-1])
        return loss_ee + 2 * loss_gripper

    @torch.no_grad()
    def sample_actions(
        self,
        state: torch.Tensor
    ) -> torch.Tensor:
        assert state.shape[1] == self.state_dim, f"state should have dim[1] = {self.state_dim} but has {x.size(1)} instead"
        return self(state)

    def forward(
        self,
        x: torch.Tensor
    ) -> torch.Tensor:
        """Return predicted action chunk of shape (B, chunk_size, action_dim)."""
        assert x.shape[1] == self.state_dim, f"x should have dim[1] = {self.state_dim} but has {x.size(1)} instead"
        # add gaussian noise to force policy to be robust to slightly off distribution states
        if self.training:
            noise = torch.randn_like(x) * 0.05
            x += noise
        x = self.l1(x)
        x, _ = self.gru(x)
        out = self.l2(x)
        return out.view(x.shape[0], self.chunk_size, self.action_dim)


PolicyType: TypeAlias = Literal["obstacle", "multitask"]


def build_policy(
    policy_type: PolicyType,
    *,
    state_dim: int,
    action_dim: int,
    chunk_size: int,
    d_model: int = 256,
    depth: int = 4
) -> BasePolicy:
    if policy_type == "obstacle":
        return ObstaclePolicy(
            action_dim=action_dim,
            state_dim=state_dim,
            # TODO: Build with your chosen specifications
            chunk_size=chunk_size,
            d_model=d_model,
            depth=depth
        )
    if policy_type == "multitask":
        return MultiTaskPolicy(
            action_dim=action_dim,
            state_dim=state_dim,
            # TODO: Build with your chosen specifications
            chunk_size=chunk_size,
            d_model=d_model
        )
    raise ValueError(f"Unknown policy type: {policy_type}")
