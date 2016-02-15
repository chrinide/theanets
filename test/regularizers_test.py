import pytest
import theanets

import util as u


@pytest.fixture
def exp():
    return theanets.Regressor([u.NUM_INPUTS, 20, u.NUM_OUTPUTS], rng=115)


def assert_progress(net, **kwargs):
    start = best = None
    for _, val in net.itertrain(
            [u.INPUTS, u.OUTPUTS],
            algorithm='sgd',
            patience=2,
            min_improvement=0.01,
            max_gradient_norm=1,
            batch_size=u.NUM_EXAMPLES,
            **kwargs):
        if start is None:
            start = best = val['loss']
        if val['loss'] < best:
            best = val['loss']
    assert best < start  # should have made progress!


def test_build_dict(exp):
    regs = theanets.regularizers.from_kwargs(
        exp, regularizers=dict(input_noise=0.01))
    assert len(regs) == 1


def test_build_list(exp):
    reg = theanets.regularizers.Regularizer.build('weight_l2', 0.01)
    regs = theanets.regularizers.from_kwargs(exp, regularizers=[reg])
    assert len(regs) == 1


@pytest.mark.parametrize('key, value', [
    ('input_noise', 0.1),
    ('input_dropout', 0.2),
    ('hidden_noise', 0.1),
    ('hidden_dropout', 0.2),
    ('noise', {'*:out': 0.1}),
    ('dropout', {'hid?:out': 0.2}),
    ('hidden_l1', 0.1),
    ('weight_l1', 0.1),
    ('weight_l2', 0.01),
    ('contractive', 0.01),
])
def test_sgd(key, value, exp):
    assert_progress(exp, **{key: value})


class RNN:
    @pytest.fixture
    def net(self):
        return theanets.recurrent.Regressor([
            u.NUM_INPUTS, (u.NUM_HID1, 'rnn'), u.NUM_OUTPUTS], rng=131)

    def test_recurrent_matching(self, net):
        regs = theanets.regularizers.from_kwargs(net)
        outputs, _ = net.build_graph(regs)
        matches = theanets.util.outputs_matching(outputs, '*:out')
        hiddens = [(n, e) for n, e in matches if e.ndim == 3]
        assert len(hiddens) == 3, [n for n, e in hiddens]

    @pytest.mark.parametrize('key, value', [
        ('recurrent_norm', dict(pattern='*:out', weight=0.1)),
        ('recurrent_state', dict(pattern='*:out', weight=0.1)),
    ])
    def test_progress(self, key, value, net):
        assert_progress(net, **{key: value})

    @pytest.mark.parametrize('key, value', [
        ('recurrent_norm', dict(pattern='*:out', weight=0.1)),
        ('recurrent_state', dict(pattern='*:out', weight=0.1)),
    ])
    def test_raises(self, key, value, net):
        with pytest.raises(theanets.util.ConfigurationError):
            assert_progress(net, **{key: value})
