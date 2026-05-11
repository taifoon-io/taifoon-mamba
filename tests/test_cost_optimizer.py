"""Tests for taifoon_mamba.cost_optimizer."""
import pytest

from taifoon_mamba.cost_optimizer import OPUS, SONNET, CostOptimizer


@pytest.fixture
def opt() -> CostOptimizer:
    return CostOptimizer()


def test_evm_routes_to_sonnet(opt):
    agent, model = opt.route({"category": "evm/eth"})
    assert agent == "coder"
    assert model == SONNET


def test_oracle_routes_to_opus(opt):
    agent, model = opt.route({"category": "oracle"})
    assert agent == "coder"
    assert model == OPUS


def test_aggregator_routes_to_opus(opt):
    agent, model = opt.route({"category": "aggregator/uniswap"})
    assert agent == "coder"
    assert model == OPUS


def test_platform_phase5_routes_to_opus(opt):
    agent, model = opt.route({"category": "platform-phase5"})
    assert agent == "coder"
    assert model == OPUS


def test_unknown_category_falls_back_to_sonnet(opt):
    agent, model = opt.route({"category": "zzz-unknown"})
    assert agent == "coder"
    assert model == SONNET


def test_empty_category_falls_back(opt):
    agent, model = opt.route({})
    assert agent == "coder"
    assert model == SONNET


def test_sol_routes_to_sonnet(opt):
    agent, model = opt.route({"category": "sol/solana"})
    assert agent == "coder"
    assert model == SONNET


def test_lambda_replay_routes_to_sonnet(opt):
    agent, model = opt.route({"category": "lambda-replay/t3rn"})
    assert agent == "coder"
    assert model == SONNET


def test_weight_tuning_returns_dict(opt):
    history = [
        {"category": "evm", "cost_usd": 0.02, "verdict": "approved"},
        {"category": "oracle", "cost_usd": 0.08, "verdict": "changes_requested"},
    ]
    result = opt.weight_tuning(history)
    assert isinstance(result, dict)
    assert "evm" in result
    assert "oracle" in result
    assert 0.0 <= result["evm"] <= 1.0


def test_weight_tuning_blocked_lowers_weight(opt):
    history = [{"category": "aggregator", "cost_usd": 0.05, "verdict": "blocked"}]
    result = opt.weight_tuning(history)
    assert result.get("aggregator", 1.0) < 1.0
