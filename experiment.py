from sapsan.core.backends.fake import FakeExperimentBackend
from sapsan.core.data.jhtdb_dataset import JHTDB128Dataset
from sapsan.core.data.sampling.equidistant_sampler import Equidistance3dSampling
from sapsan.core.estimator.cnn.spacial_3d_encoder import Spacial3dEncoderNetworkEstimator, Spacial3dEncoderNetworkEstimatorConfiguration
from sapsan.core.experiments.evaluation_3d import Evaluation3dExperiment
from sapsan.core.experiments.training import TrainingExperiment


def run():
    dataset_root_dir = "/Users/icekhan/Documents/development/myprojects/sapsan/repo/Sapsan/dataset"
    CHECKPOINT_DATA_SIZE = 128
    SAMPLE_TO = 32
    GRID_SIZE = 8
    features = ['u', 'b', 'a',
                'du0', 'du1', 'du2',
                'db0', 'db1', 'db2',
                'da0', 'da1', 'da2']
    labels = ['tn']

    sampler = Equidistance3dSampling(CHECKPOINT_DATA_SIZE, SAMPLE_TO)

    training_experiment_name = "Training experiment"
    estimator = Spacial3dEncoderNetworkEstimator(
        config=Spacial3dEncoderNetworkEstimatorConfiguration(n_epochs=100, grid_dim=GRID_SIZE)
    )
    x, y = JHTDB128Dataset(path=dataset_root_dir,
                           features=features,
                           labels=labels,
                           checkpoints=[0.0, 0.01, 0.25],
                           grid_size=GRID_SIZE,
                           checkpoint_data_size=CHECKPOINT_DATA_SIZE,
                           sampler=sampler).load()

    training_experiment = TrainingExperiment(name=training_experiment_name,
                                             backend=FakeExperimentBackend(training_experiment_name),
                                             model=estimator,
                                             inputs=x, targets=y)
    training_experiment.run()

    x, y = JHTDB128Dataset(path=dataset_root_dir,
                           features=features,
                           labels=labels,
                           checkpoints=[0.025],
                           grid_size=GRID_SIZE,
                           checkpoint_data_size=CHECKPOINT_DATA_SIZE,
                           sampler=sampler).load()

    evaluation_experiment_name = "Evaluation experiment"
    evaluation_experiment = Evaluation3dExperiment(name=evaluation_experiment_name,
                                                   backend=FakeExperimentBackend(evaluation_experiment_name),
                                                   model=training_experiment.model,
                                                   inputs=x, targets=y,
                                                   n_output_channels=3,
                                                   grid_size=GRID_SIZE,
                                                   checkpoint_data_size=SAMPLE_TO)

    evaluation_experiment.run()


if __name__ == '__main__':
    run()
