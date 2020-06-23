import torch
import torch.nn as nn
import torch.nn.functional as F

from pytorch_lightning.core.lightning import LightningModule
from pl_develop.datasets import TrialMNIST, PATH_DATASETS
from pl_develop import ConfigureOptimizersPool
from pl_develop.model_test_dataloaders import TestDataloaderVariations
from pl_develop.model_test_epoch_ends import TestEpochEndVariations
from pl_develop.model_test_steps import TestStepVariations
from pl_develop import TrainDataloaderVariations
from pl_develop import TrainingStepVariations
from pl_develop.model_utilities import ModelTemplateUtils, ModelTemplateData
from pl_develop import ValDataloaderVariations
from pl_develop.model_valid_epoch_ends import ValidationEpochEndVariations
from pl_develop import ValidationStepVariations


class EvalModelTemplate(
    ModelTemplateData,
    ModelTemplateUtils,
    TrainingStepVariations,
    ValidationStepVariations,
    ValidationEpochEndVariations,
    TestStepVariations,
    TestEpochEndVariations,
    TrainDataloaderVariations,
    ValDataloaderVariations,
    TestDataloaderVariations,
    ConfigureOptimizersPool,
    LightningModule
):
    """
    This template houses all  combinations of model  configurations  we want to test

    >>> model = EvalModelTemplate()
    """

    def __init__(self,
                 *args,
                 drop_prob: float = 0.2,
                 batch_size: int = 32,
                 in_features: int = 28 * 28,
                 learning_rate: float = 0.001 * 8,
                 optimizer_name: str = 'adam',
                 data_root: str = PATH_DATASETS,
                 out_features: int = 10,
                 hidden_dim: int = 1000,
                 b1: float = 0.5,
                 b2: float = 0.999,
                 **kwargs) -> object:
        # init superclass
        super().__init__()
        self.save_hyperparameters()

        self.drop_prob = drop_prob
        self.batch_size = batch_size
        self.in_features = in_features
        self.learning_rate = learning_rate
        self.optimizer_name = optimizer_name
        self.data_root = data_root
        self.out_features = out_features
        self.hidden_dim = hidden_dim
        self.b1 = b1
        self.b2 = b2

        # if you specify an example input, the summary will show input/output for each layer
        # TODO: to be fixed in #1773
        # self.example_input_array = torch.rand(5, 28 * 28)

        # build model
        self.__build_model()

    def __build_model(self):
        """
        Simple model for testing
        :return:
        """
        self.c_d1 = nn.Linear(
            in_features=self.in_features,
            out_features=self.hidden_dim
        )
        self.c_d1_bn = nn.BatchNorm1d(self.hidden_dim)
        self.c_d1_drop = nn.Dropout(self.drop_prob)

        self.c_d2 = nn.Linear(
            in_features=self.hidden_dim,
            out_features=self.out_features
        )

    def forward(self, x):
        x = self.c_d1(x)
        x = torch.tanh(x)
        x = self.c_d1_bn(x)
        x = self.c_d1_drop(x)

        x = self.c_d2(x)
        logits = F.log_softmax(x, dim=1)

        return logits

    def loss(self, labels, logits):
        nll = F.nll_loss(logits, labels)
        return nll

    def prepare_data(self):
        TrialMNIST(root=self.data_root, train=True, download=True)

    @staticmethod
    def get_default_hparams(continue_training: bool = False, hpc_exp_number: int = 0) -> dict:
        args = dict(
            drop_prob=0.2,
            batch_size=32,
            in_features=28 * 28,
            learning_rate=0.001 * 8,
            optimizer_name='adam',
            data_root=PATH_DATASETS,
            out_features=10,
            hidden_dim=1000,
            b1=0.5,
            b2=0.999,
        )

        if continue_training:
            args.update(
                test_tube_do_checkpoint_load=True,
                hpc_exp_number=hpc_exp_number,
            )

        return args