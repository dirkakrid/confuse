import confit
from . import _root, unittest


class ValidConfigTest(unittest.TestCase):
    def test_validate_simple_dict(self):
        config = _root({'foo': 5})
        valid = config.validate({'foo': confit.Integer()})
        self.assertEqual(valid['foo'], 5)

    def test_default_value(self):
        config = _root({})
        valid = config.validate({'foo': confit.Integer(8)})
        self.assertEqual(valid['foo'], 8)

    def test_undeclared_key_raises_keyerror(self):
        config = _root({'foo': 5})
        valid = config.validate({'foo': confit.Integer()})
        with self.assertRaises(KeyError):
            valid['bar']

    def test_undeclared_key_ignored_from_input(self):
        config = _root({'foo': 5, 'bar': 6})
        valid = config.validate({'foo': confit.Integer()})
        with self.assertRaises(KeyError):
            valid['bar']

    def test_int_template_shortcut(self):
        config = _root({'foo': 5})
        valid = config.validate({'foo': int})
        self.assertEqual(valid['foo'], 5)

    def test_int_default_shortcut(self):
        config = _root({})
        valid = config.validate({'foo': 9})
        self.assertEqual(valid['foo'], 9)

    def test_attribute_access(self):
        config = _root({'foo': 5})
        valid = config.validate({'foo': confit.Integer()})
        self.assertEqual(valid.foo, 5)

    def test_missing_required_value_raises_error_on_validate(self):
        config = _root({})
        with self.assertRaises(confit.NotFoundError):
            config.validate({'foo': confit.Integer(required=True)})

    def test_wrong_type_raises_error_on_validate(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.ConfigError):
            config.validate({'foo': confit.Integer()})

    def test_validate_individual_value(self):
        config = _root({'foo': 5})
        valid = config['foo'].validate(confit.Integer())
        self.assertEqual(valid, 5)

    def test_nested_dict_template(self):
        config = _root({
            'foo': {'bar': 9},
        })
        valid = config.validate({
            'foo': {'bar': confit.Integer()},
        })
        self.assertEqual(valid['foo']['bar'], 9)

    def test_nested_attribute_access(self):
        config = _root({
            'foo': {'bar': 8},
        })
        valid = config.validate({
            'foo': {'bar': confit.Integer()},
        })
        self.assertEqual(valid.foo.bar, 8)


class AsTemplateTest(unittest.TestCase):
    def test_plain_int_as_template(self):
        typ = confit.as_template(int)
        self.assertIsInstance(typ, confit.Integer)
        self.assertEqual(typ.default, None)

    def test_concrete_int_as_template(self):
        typ = confit.as_template(2)
        self.assertIsInstance(typ, confit.Integer)
        self.assertEqual(typ.default, 2)

    def test_plain_string_as_template(self):
        typ = confit.as_template(str)
        self.assertIsInstance(typ, confit.String)
        self.assertEqual(typ.default, None)

    def test_concrete_string_as_template(self):
        typ = confit.as_template('foo')
        self.assertIsInstance(typ, confit.String)
        self.assertEqual(typ.default, 'foo')

    def test_dict_as_template(self):
        typ = confit.as_template({'key': 9})
        self.assertIsInstance(typ, confit.MappingTemplate)
        self.assertIsInstance(typ.subtemplates['key'], confit.Integer)
        self.assertEqual(typ.subtemplates['key'].default, 9)

    def test_nested_dict_as_template(self):
        typ = confit.as_template({'outer': {'inner': 2}})
        self.assertIsInstance(typ, confit.MappingTemplate)
        self.assertIsInstance(typ.subtemplates['outer'],
                              confit.MappingTemplate)
        self.assertIsInstance(typ.subtemplates['outer'].subtemplates['inner'],
                              confit.Integer)
        self.assertEqual(typ.subtemplates['outer'].subtemplates['inner']
                         .default, 2)


class StringTemplateTest(unittest.TestCase):
    def test_validate_string(self):
        config = _root({'foo': 'bar'})
        valid = config.validate({'foo': confit.String()})
        self.assertEqual(valid['foo'], 'bar')

    def test_string_default_value(self):
        config = _root({})
        valid = config.validate({'foo': confit.String('baz')})
        self.assertEqual(valid['foo'], 'baz')

    def test_pattern_matching(self):
        config = _root({'foo': 'bar', 'baz': 'zab'})
        valid = config.validate({'foo': confit.String(pattern='^ba.$')})
        self.assertEqual(valid['foo'], 'bar')
        with self.assertRaises(confit.ConfigValueError):
            config.validate({'baz': confit.String(pattern='!')})

    def test_string_template_shortcut(self):
        config = _root({'foo': 'bar'})
        valid = config.validate({'foo': str})
        self.assertEqual(valid['foo'], 'bar')

    def test_string_default_shortcut(self):
        config = _root({})
        valid = config.validate({'foo': 'bar'})
        self.assertEqual(valid['foo'], 'bar')

    def test_check_string_type(self):
        config = _root({'foo': 5})
        with self.assertRaises(confit.ConfigError):
            config.validate({'foo': confit.String()})
