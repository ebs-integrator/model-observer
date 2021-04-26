# Model Observer

**Model Observer** is a Django package that provides functionality to track events of the model. Based on django signals. 

**ModelObserver** class will observe model behavior and triggers different signals.
## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install model_observer.

```bash
pip install model_observer
```

## Available signals 
```python
class ModelObserver:
    _available_signal_types = ('pre_init', 'post_init', 'pre_save', 'post_save',
                               'pre_delete', 'post_delete', 'm2m_changed',
                               'pre_migrate', 'post_migrate')
```

## Usage

```python
from model_observer.model import ModelObserver

class Blog(Model, ModelObserver):
    title = models.CharField(max_length=50)

    def on_delete(self, **kwargs):
        print('Object was deleted!')
        print('self', self.__dict__)
        print('kwargs', kwargs)

    def on_create(self, **kwargs):
        print('Object was created!')
        print('self', self.__dict__)
        print('kwargs', kwargs)

    def on_update(self, **kwargs):
        print('Object was updated!')
        print('self', self.__dict__)
        print('kwargs', kwargs)
```

### Create object
```python
from blogs.models import Blog
blog = Blog.objects.create(title='test1')
```
**Output**
```
Object was created!
self {'_state': <django.db.models.base.ModelState object at 0x0000013FDE855640>, 'id': 2, 'title': 'test1'}
kwargs {'signal': <django.db.models.signals.ModelSignal object at 0x0000013FDD6A93A0>, 'sender': <class 'blogs.models.Blog'>, 'instance': <Blog: Blog object (2)>, 'created': True, 'update_fields': None, 'raw': False, 'using': 'default'}
```

### Update object
```python
from blogs.models import Blog
blog = Blog.objects.get(pk=1)
blog.title = 'test 1!'
blog.save()
```
**Output**
```
Object was updated!
self {'_state': <django.db.models.base.ModelState object at 0x0000024B609A8FA0>, 'id': 1, 'title': 'test 1!', '_pre_save_instance': <Blog: Blog object (1)>, '_pre_delete_instance': <Blog: Blog object (1)>}
kwargs {'signal': <django.db.models.signals.ModelSignal object at 0x0000024B5F69FCD0>, 'sender': <class 'blogs.models.Blog'>, 'instance': <Blog: Blog object (1)>, 'created': False, 'update_fields': None, 'raw': False, 'using': 'default'}

```

### Delete object
```python
from blogs.models import Blog
blog = Blog.objects.get(pk=3)
blog.delete()
```
**Output**
```
Object was deleted!
self {'_state': <django.db.models.base.ModelState object at 0x00000182BA476AC0>, 'id': 3, 'title': 'test1'}
kwargs {'signal': <django.db.models.signals.ModelSignal object at 0x00000182B92985E0>, 'sender': <class 'blogs.models.Blog'>, 'instance': <Blog: Blog object (3)>, 'using': 'default'}
(1, {'blogs.Blog': 1})
```


### Observe the object field
**Integration**
```python
class Blog(models.Model, ModelObserver):
    ...

    def title_changed(self, **kwargs):
        print('Field `title` was changed!')
        print('self', self.__dict__)
        print('kwargs', kwargs)
        
        instance = kwargs.get('instance')  # Work with instance
        ...

```
```python
from blogs.models import Blog
blog = Blog.objects.first()
blog.title = 'Test 2!'
blog.save()
```
**Output**
```
Field `title` was changed!
self {'_state': <django.db.models.base.ModelState object at 0x0000023ED4BF4700>, 'id': 4, 'title': 'Test 2!', '_pre_save_instance': <Blog: Blog object (4)>, '_pre_delete_instance': <Blog: Blog object (4)>}
kwargs {'signal': <django.db.models.signals.ModelSignal object at 0x0000023ED3A48280>, 'sender': <class 'blogs.models.Blog'>, 'instance': <Blog: Blog object (4)>, 'raw': False, 'using': 'default', 'update_fields': None}

```


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GNU](https://choosealicense.com/licenses/gpl-3.0/)