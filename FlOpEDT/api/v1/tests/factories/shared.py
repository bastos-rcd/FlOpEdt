import factory


class PostGenerationWithCounter(factory.PostGeneration):
    # no need of evaluate? https://github.com/FactoryBoy/factory_boy/issues/936
    # pylint: disable=abstract-method
    def call(self, instance, step, context):
        create = step.builder.strategy == factory.enums.CREATE_STRATEGY
        return self.function(instance, step, create, context.value, **context.extra)
