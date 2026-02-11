from rayforce import types as t


class TestArithmeticMixin:
    def test_vector_add(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 2, 3])
        v2 = t.Vector(ray_type=t.I64, items=[4, 5, 6])
        assert (v1 + v2).to_python() == [5, 7, 9]

    def test_vector_subtract(self):
        v1 = t.Vector(ray_type=t.I64, items=[10, 20, 30])
        v2 = t.Vector(ray_type=t.I64, items=[1, 2, 3])
        assert (v1 - v2).to_python() == [9, 18, 27]

    def test_vector_multiply(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3])
        assert (v * 2).to_python() == [2, 4, 6]

    def test_vector_fdivide(self):
        v = t.Vector(ray_type=t.I64, items=[5, 10, 15])
        assert (v / 2).to_python() == [t.F64(2.5), t.F64(5), t.F64(7.5)]

    def test_vector_truedivide(self):
        v = t.Vector(ray_type=t.I64, items=[5, 10, 15])
        assert (v // 2).to_python() == [2, 5, 7]

    def test_scalar_add(self):
        assert (t.I64(10) + t.I64(20)).to_python() == 30

    def test_scalar_subtract(self):
        assert (t.I64(30) - t.I64(10)).to_python() == 20

    def test_scalar_multiply(self):
        assert (t.I64(5) * 3).to_python() == 15

    def test_scalar_divide(self):
        assert (t.I64(20) / 4).to_python() == 5

    def test_scalar_modulo(self):
        assert (t.I64(17) % 5).to_python() == 2


class TestComparisonMixin:
    def test_vector_less_than(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 5, 10])
        v2 = t.Vector(ray_type=t.I64, items=[2, 5, 8])
        assert (v1 < v2).to_python() == [True, False, False]

    def test_vector_greater_than(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 5, 10])
        v2 = t.Vector(ray_type=t.I64, items=[2, 5, 8])
        assert (v1 > v2).to_python() == [False, False, True]

    def test_vector_less_equal(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 5, 10])
        v2 = t.Vector(ray_type=t.I64, items=[2, 5, 8])
        assert (v1 <= v2).to_python() == [True, True, False]

    def test_vector_greater_equal(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 5, 10])
        v2 = t.Vector(ray_type=t.I64, items=[2, 5, 8])
        assert (v1 >= v2).to_python() == [False, True, True]

    def test_vector_eq(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 5, 10])
        v2 = t.Vector(ray_type=t.I64, items=[2, 5, 8])
        assert v1.eq(v2).to_python() == [False, True, False]

    def test_vector_ne(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 5, 10])
        v2 = t.Vector(ray_type=t.I64, items=[2, 5, 8])
        assert v1.ne(v2).to_python() == [True, False, True]

    def test_vector_and(self):
        v1 = t.Vector(ray_type=t.B8, items=[True, False, True])
        v2 = t.Vector(ray_type=t.B8, items=[True, True, False])
        assert v1.and_(v2).to_python() == [True, False, False]

    def test_vector_or(self):
        v1 = t.Vector(ray_type=t.B8, items=[True, False, False])
        v2 = t.Vector(ray_type=t.B8, items=[False, False, True])
        assert v1.or_(v2).to_python() == [True, False, True]

    def test_vector_not(self):
        v = t.Vector(ray_type=t.B8, items=[True, False, True])
        assert v.not_().to_python() == [False, True, False]

    def test_scalar_less_than(self):
        assert (t.I64(5) < t.I64(10)).to_python() is True

    def test_scalar_greater_than(self):
        assert (t.I64(15) > t.I64(10)).to_python() is True


class TestAggregationMixin:
    def test_vector_sum(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4, 5])
        assert v.sum().to_python() == 15

    def test_vector_average(self):
        v = t.Vector(ray_type=t.F64, items=[1.0, 2.0, 3.0, 4.0, 5.0])
        assert v.average().to_python() == 3.0

    def test_vector_min(self):
        v = t.Vector(ray_type=t.I64, items=[5, 2, 8, 1, 9])
        assert v.min().to_python() == 1

    def test_vector_max(self):
        v = t.Vector(ray_type=t.I64, items=[5, 2, 8, 1, 9])
        assert v.max().to_python() == 9

    def test_vector_median(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4, 5])
        assert v.median().to_python() == 3.0

    def test_scalar_ceil(self):
        assert t.F64(3.2).ceil().to_python() == 4.0

    def test_scalar_floor(self):
        assert t.F64(3.8).floor().to_python() == 3.0

    def test_scalar_round(self):
        assert t.F64(3.5).round().to_python() == 4.0

    def test_vector_ceil(self):
        v = t.Vector(ray_type=t.F64, items=[1.2, 2.5, 3.8])
        assert v.ceil().to_python() == [2.0, 3.0, 4.0]

    def test_vector_floor(self):
        v = t.Vector(ray_type=t.F64, items=[1.2, 2.5, 3.8])
        assert v.floor().to_python() == [1.0, 2.0, 3.0]


class TestElementAccessMixin:
    def test_vector_first(self):
        v = t.Vector(ray_type=t.I64, items=[10, 20, 30])
        assert v.first().to_python() == 10

    def test_vector_last(self):
        v = t.Vector(ray_type=t.I64, items=[10, 20, 30])
        assert v.last().to_python() == 30

    def test_vector_take(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4, 5])
        assert v.take(3).to_python() == [1, 2, 3]

    def test_vector_take_negative(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4, 5])
        assert v.take(-2).to_python() == [4, 5]

    def test_vector_at(self):
        v = t.Vector(ray_type=t.I64, items=[10, 20, 30])
        assert v.at(1).to_python() == 20


class TestSetOperationMixin:
    def test_vector_union(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 2, 3])
        v2 = t.Vector(ray_type=t.I64, items=[3, 4, 5])
        assert set(v1.union(v2).to_python()) == {1, 2, 3, 4, 5}

    def test_vector_sect(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4])
        v2 = t.Vector(ray_type=t.I64, items=[3, 4, 5, 6])
        assert set(v1.sect(v2).to_python()) == {3, 4}

    def test_vector_except(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4])
        v2 = t.Vector(ray_type=t.I64, items=[3, 4, 5])
        assert set(v1.except_(v2).to_python()) == {1, 2}


class TestSearchMixin:
    def test_vector_in(self):
        haystack = t.Vector(ray_type=t.I64, items=[2, 4, 6])
        needle = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4, 5])
        assert needle.in_(haystack).to_python() == [True, True, False]

    def test_vector_find(self):
        v = t.Vector(ray_type=t.I64, items=[10, 20, 30, 40])
        assert v.find(30).to_python() == 2

    def test_vector_filter(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4, 5])
        mask = t.Vector(ray_type=t.B8, items=[True, False, True, False, True])
        assert v.filter(mask).to_python() == [1, 3, 5]

    def test_vector_within(self):
        v = t.Vector(ray_type=t.I64, items=[1, 5, 10, 15, 20])
        range_vec = t.Vector(ray_type=t.I64, items=[5, 15])
        assert v.within(range_vec).to_python() == [False, True, True, True, False]


class TestFunctionalMixin:
    def test_vector_map_with_operation(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3])
        assert v.map(t.Operation.NEGATE).to_python() == [-1, -2, -3]


class TestSortMixin:
    def test_vector_asc(self):
        v = t.Vector(ray_type=t.I64, items=[3, 1, 4, 1, 5])
        assert v.asc().to_python() == [1, 1, 3, 4, 5]

    def test_vector_desc(self):
        v = t.Vector(ray_type=t.I64, items=[3, 1, 4, 1, 5])
        assert v.desc().to_python() == [5, 4, 3, 1, 1]

    def test_vector_iasc(self):
        v = t.Vector(ray_type=t.I64, items=[3, 1, 4])
        assert v.iasc().to_python() == [1, 0, 2]

    def test_vector_idesc(self):
        v = t.Vector(ray_type=t.I64, items=[3, 1, 4])
        assert v.idesc().to_python() == [2, 0, 1]

    def test_vector_rank(self):
        v = t.Vector(ray_type=t.I64, items=[30, 10, 20])
        assert v.rank().to_python() == [2, 0, 1]

    def test_vector_reverse(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3])
        assert v.reverse().to_python() == [3, 2, 1]

    def test_vector_negate(self):
        v = t.Vector(ray_type=t.I64, items=[1, -2, 3])
        assert v.negate().to_python() == [-1, 2, -3]


class TestMappableMixin:
    def test_dict_key(self):
        d = t.Dict({"a": 1, "b": 2, "c": 3})
        assert set(d.key().to_python()) == {"a", "b", "c"}

    def test_dict_value(self):
        d = t.Dict({"a": 1, "b": 2, "c": 3})
        assert set(d.value().to_python()) == {1, 2, 3}
