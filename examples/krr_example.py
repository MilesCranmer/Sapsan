from sapsan.core.backends.fake import FakeExperimentBackend
from sapsan.core.data.flatten_dataset import FlattenFrom3dDataset
from sapsan.core.data.sampling.equidistant_sampler import Equidistance3dSampling
from sapsan.core.estimator import KrrEstimator, KrrEstimatorConfiguration
from sapsan.core.experiments.evaluation_flatten import EvaluationFlattenExperiment
from sapsan.core.experiments.training import TrainingExperiment


def run():
    dataset_root_dir = "/Users/icekhan/Documents/development/myprojects/sapsan/repo/Sapsan/dataset"
    CHECKPOINT_DATA_SIZE = 128
    SAMPLE_TO = 16
    features = ['u', 'b', 'a',
                'du0', 'du1', 'du2',
                'db0', 'db1', 'db2',
                'da0', 'da1', 'da2']
    labels = ['tn']
    train_checkpoints = [0]

    sampler = Equidistance3dSampling(CHECKPOINT_DATA_SIZE, SAMPLE_TO)
    experiment_name = "KRR experiment"

    tracker_backend = FakeExperimentBackend(experiment_name)

    estimator = KrrEstimator(
        config=KrrEstimatorConfiguration().from_yaml()
    )
    x, y = FlattenFrom3dDataset(path=dataset_root_dir,
                                features=features,
                                labels=labels,
                                checkpoints=train_checkpoints,
                                sampler=sampler,
                                label_channels=[0]).load()

    training_experiment = TrainingExperiment(name="{} train".format(experiment_name),
                                             backend=tracker_backend,
                                             model=estimator,
                                             inputs=x, targets=y)
    training_experiment.run()

    evaluation_experiment = EvaluationFlattenExperiment(name="{} evaluation".format(experiment_name),
                                                        backend=tracker_backend,
                                                        model=training_experiment.model,
                                                        inputs=x, targets=y,
                                                        n_output_channels=3,
                                                        checkpoint_data_size=CHECKPOINT_DATA_SIZE,
                                                        grid_size=SAMPLE_TO,
                                                        checkpoints=train_checkpoints)

    evaluation_experiment.run()


if __name__ == '__main__':
    run()
