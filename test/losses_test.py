import theanets

import util


class TestBuild:
    def test_build_mse(self):
        l = theanets.Loss.build('mse', in_dim=2, out_dim=1)
        assert callable(l)
        assert len(l.variables) == 2

    def test_build_mae(self):
        l = theanets.Loss.build('mae', in_dim=2)
        assert callable(l)
        assert len(l.variables) == 1

    def test_build_mae_weighted(self):
        l = theanets.Loss.build('mae', in_dim=2, weighted=True)
        assert callable(l)
        assert len(l.variables) == 2


class TestNetwork(util.Base):
    def test_kl(self):
        self.exp = theanets.Regressor(
            layers=(self.NUM_INPUTS, 10, (self.NUM_OUTPUTS, 'softmax')), loss='kl')
        assert self.exp.loss.__class__.__name__ == 'KullbackLeiblerDivergence'
        self.assert_progress('sgd', [self.INPUTS, abs(self.OUTPUTS)])

    def test_hinge(self):
        self.exp = theanets.Network(
            layers=(self.NUM_INPUTS, 10, self.NUM_CLASSES),
            in_dim=2, out_dim=1, loss='hinge')
        name = self.exp.loss.__class__.__name__
        assert name == 'Hinge', name
        self.assert_progress('sgd', [self.INPUTS, self.CLASSES])

    def test_mae(self):
        self.exp = theanets.Autoencoder((self.NUM_INPUTS, self.NUM_INPUTS), loss='mae')
        assert self.exp.loss.__class__.__name__ == 'MeanAbsoluteError'
        self.assert_progress('sgd', [self.INPUTS])
