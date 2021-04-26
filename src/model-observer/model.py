from abc import abstractmethod
from django.db.models import signals
from django.utils.translation import gettext as _


class ModelObserver:
    """
        This class will observe model behavior and triggers different signals.
    """

    # Signal types
    _available_signal_types = ('pre_init', 'post_init', 'pre_save', 'post_save',
                               'pre_delete', 'post_delete', 'm2m_changed',
                               'pre_migrate', 'post_migrate')

    # Model default signals of type: method_name as key and signal_type as value
    DEFAULT_SIGNALS: dict = {
        'pre_save': '_pre_saving',
        'post_save': '_post_saving',
        'post_delete': 'on_delete',
    }

    # Model custom signals of type: method_name as key and signal_type as value
    SIGNALS: dict = {}

    # Suffix for changed fields. Will be used for method call in _pre_saving
    # method.
    SUFFIX = '_changed'

    def __init__(self):
        self._signals()

    def _pre_saving(self, **kwargs):
        # Arguments
        instance = kwargs.get('instance')

        if not instance.pk:
            # In case when object is creating.
            return True

        # Getting object before changes
        model = instance.__class__

        try:
            previous = model.objects.get(pk=instance.pk)
            instance._pre_save_instance = previous
            instance._pre_delete_instance = previous
        except model.DoesNotExist:
            previous = instance
            instance._pre_save_instance = previous
            instance._pre_delete_instance = previous

        # Getting all model fields
        fields = instance._meta.concrete_fields

        for field in fields:
            name = field.name
            current_value = getattr(instance, name)
            previous_value = getattr(previous, name)
            method = getattr(self, f'{name}{self.SUFFIX}', None)

            if current_value != previous_value and method:
                method(**kwargs)

    def _post_saving(self, **kwargs):
        if kwargs.get('created', False):
            return self.on_create(**kwargs)

        return self.on_update(**kwargs)

    @abstractmethod
    def on_create(self, **kwargs):
        ...

    @abstractmethod
    def on_update(self, **kwargs):
        ...

    @abstractmethod
    def on_delete(self, **kwargs):
        ...

    def _get_all_signals(self):
        all_signals = self.DEFAULT_SIGNALS.copy()
        all_signals.update(self.SIGNALS)

    def _signals(self):
        all_signals = self.DEFAULT_SIGNALS.copy()
        all_signals.update(self.SIGNALS)

        for signal_type, method_name in all_signals.items():
            # Verifying that method was indicated in SIGNALS model param.
            receiver = getattr(self, method_name, None)
            if not receiver:
                raise AttributeError(_('\'%(name)s\' model has no method \'%(method)s\'' %
                                       ({'name': self.__class__.__name__, 'method': method_name})))

            # Initialize signal by calling a method.
            self._signal(signal_type, receiver)

    def _signal(self, signal_type, receiver):
        # Verifying for existence of signal type.
        signal = getattr(signals, signal_type, None)
        if not signal:
            raise AttributeError(_('Signals don\'t have signal of type \'%(first)s\'. '
                                   'Available signal types: %(second)s' %
                                   ({'first': signal_type, 'second': self._available_signal_types})))

        # Setting up dispatch_uid
        dispatch_uid = f'{self.__class__.__name__}_{signal_type}'

        # Initializing signal
        signal.connect(receiver=receiver, dispatch_uid=dispatch_uid,
                       weak=False, sender=self.__class__)
