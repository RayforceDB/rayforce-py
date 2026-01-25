from rayforce import types as t


class TestArithmeticMixin:
    def test_vector_add(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 2, 3])
        v2 = t.Vector(ray_type=t.I64, items=[4, 5, 6])
        result = v1 + v2
        assert result.to_python() == [5, 7, 9]

    def test_vector_subtract(self):
        v1 = t.Vector(ray_type=t.I64, items=[10, 20, 30])
        v2 = t.Vector(ray_type=t.I64, items=[1, 2, 3])
        result = v1 - v2
        assert result.to_python() == [9, 18, 27]

    def test_vector_multiply(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3])
        result = v * 2
        assert result.to_python() == [2, 4, 6]

    def test_vector_fdivide(self):
        v = t.Vector(ray_type=t.I64, items=[5, 10, 15])
        result = v / 2
        assert result.to_python() == [t.F64(2.5), t.F64(5), t.F64(7.5)]

    def test_vector_truedivide(self):
        v = t.Vector(ray_type=t.I64, items=[5, 10, 15])
        result = v // 2
        assert result.to_python() == [2, 5, 7]

    def test_scalar_add(self):
        s1 = t.I64(10)
        s2 = t.I64(20)
        result = s1 + s2
        assert result.to_python() == 30

    def test_scalar_subtract(self):
        s1 = t.I64(30)
        s2 = t.I64(10)
        result = s1 - s2
        assert result.to_python() == 20

    def test_scalar_multiply(self):
        s = t.I64(5)
        result = s * 3
        assert result.to_python() == 15

    def test_scalar_divide(self):
        s = t.I64(20)
        result = s / 4
        assert result.to_python() == 5

    def test_scalar_modulo(self):
        s = t.I64(17)
        result = s % 5
        assert result.to_python() == 2


class TestComparisonMixin:
    def test_vector_less_than(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 5, 10])
        v2 = t.Vector(ray_type=t.I64, items=[2, 5, 8])
        result = v1 < v2
        assert result.to_python() == [True, False, False]

    def test_vector_greater_than(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 5, 10])
        v2 = t.Vector(ray_type=t.I64, items=[2, 5, 8])
        result = v1 > v2
        assert result.to_python() == [False, False, True]

    def test_vector_less_equal(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 5, 10])
        v2 = t.Vector(ray_type=t.I64, items=[2, 5, 8])
        result = v1 <= v2
        assert result.to_python() == [True, True, False]

    def test_vector_greater_equal(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 5, 10])
        v2 = t.Vector(ray_type=t.I64, items=[2, 5, 8])
        result = v1 >= v2
        assert result.to_python() == [False, True, True]

    def test_vector_eq(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 5, 10])
        v2 = t.Vector(ray_type=t.I64, items=[2, 5, 8])
        result = v1.eq(v2)
        assert result.to_python() == [False, True, False]

    def test_vector_ne(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 5, 10])
        v2 = t.Vector(ray_type=t.I64, items=[2, 5, 8])
        result = v1.ne(v2)
        assert result.to_python() == [True, False, True]

    def test_vector_and(self):
        v1 = t.Vector(ray_type=t.B8, items=[True, False, True])
        v2 = t.Vector(ray_type=t.B8, items=[True, True, False])
        result = v1.and_(v2)
        assert result.to_python() == [True, False, False]

    def test_vector_or(self):
        v1 = t.Vector(ray_type=t.B8, items=[True, False, False])
        v2 = t.Vector(ray_type=t.B8, items=[False, False, True])
        result = v1.or_(v2)
        assert result.to_python() == [True, False, True]

    def test_vector_not(self):
        v = t.Vector(ray_type=t.B8, items=[True, False, True])
        result = v.not_()
        assert result.to_python() == [False, True, False]

    def test_scalar_less_than(self):
        s1 = t.I64(5)
        s2 = t.I64(10)
        result = s1 < s2
        assert result.to_python() is True

    def test_scalar_greater_than(self):
        s1 = t.I64(15)
        s2 = t.I64(10)
        result = s1 > s2
        assert result.to_python() is True


class TestAggregationMixin:
    def test_vector_sum(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4, 5])
        result = v.sum()
        assert result.to_python() == 15

    def test_vector_average(self):
        v = t.Vector(ray_type=t.F64, items=[1.0, 2.0, 3.0, 4.0, 5.0])
        result = v.average()
        assert result.to_python() == 3.0

    def test_vector_min(self):
        v = t.Vector(ray_type=t.I64, items=[5, 2, 8, 1, 9])
        result = v.min()
        assert result.to_python() == 1

    def test_vector_max(self):
        v = t.Vector(ray_type=t.I64, items=[5, 2, 8, 1, 9])
        result = v.max()
        assert result.to_python() == 9

    def test_vector_median(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4, 5])
        result = v.median()
        assert result.to_python() == 3.0

    def test_scalar_ceil(self):
        s = t.F64(3.2)
        result = s.ceil()
        assert result.to_python() == 4.0

    def test_scalar_floor(self):
        s = t.F64(3.8)
        result = s.floor()
        assert result.to_python() == 3.0

    def test_scalar_round(self):
        s = t.F64(3.5)
        result = s.round()
        assert result.to_python() == 4.0

    def test_vector_ceil(self):
        v = t.Vector(ray_type=t.F64, items=[1.2, 2.5, 3.8])
        result = v.ceil()
        assert result.to_python() == [2.0, 3.0, 4.0]

    def test_vector_floor(self):
        v = t.Vector(ray_type=t.F64, items=[1.2, 2.5, 3.8])
        result = v.floor()
        assert result.to_python() == [1.0, 2.0, 3.0]


class TestElementAccessMixin:
    def test_vector_first(self):
        v = t.Vector(ray_type=t.I64, items=[10, 20, 30])
        result = v.first()
        assert result.to_python() == 10

    def test_vector_last(self):
        v = t.Vector(ray_type=t.I64, items=[10, 20, 30])
        result = v.last()
        assert result.to_python() == 30

    def test_vector_take(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4, 5])
        result = v.take(3)
        assert result.to_python() == [1, 2, 3]

    def test_vector_take_negative(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4, 5])
        result = v.take(-2)
        assert result.to_python() == [4, 5]

    def test_vector_at(self):
        v = t.Vector(ray_type=t.I64, items=[10, 20, 30])
        result = v.at(1)
        assert result.to_python() == 20


class TestSetOperationMixin:
    def test_vector_union(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 2, 3])
        v2 = t.Vector(ray_type=t.I64, items=[3, 4, 5])
        result = v1.union(v2)
        assert set(result.to_python()) == {1, 2, 3, 4, 5}

    def test_vector_sect(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4])
        v2 = t.Vector(ray_type=t.I64, items=[3, 4, 5, 6])
        result = v1.sect(v2)
        assert set(result.to_python()) == {3, 4}

    def test_vector_except(self):
        v1 = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4])
        v2 = t.Vector(ray_type=t.I64, items=[3, 4, 5])
        result = v1.except_(v2)
        assert set(result.to_python()) == {1, 2}


class TestSearchMixin:
    def test_vector_in(self):
        # Check if elements of haystack are in needle
        haystack = t.Vector(ray_type=t.I64, items=[2, 4, 6])
        needle = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4, 5])
        result = needle.in_(haystack)
        # haystack elements [2, 4, 6] checked against needle [1, 2, 3, 4, 5]
        # 2 in needle? True, 4 in needle? True, 6 in needle? False
        assert [x.to_python() for x in result] == [True, True, False]

    def test_vector_find(self):
        v = t.Vector(ray_type=t.I64, items=[10, 20, 30, 40])
        result = v.find(30)
        assert result.to_python() == 2

    def test_vector_filter(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3, 4, 5])
        mask = t.Vector(ray_type=t.B8, items=[True, False, True, False, True])
        result = v.filter(mask)
        assert result.to_python() == [1, 3, 5]

    def test_vector_within(self):
        v = t.Vector(ray_type=t.I64, items=[1, 5, 10, 15, 20])
        range_vec = t.Vector(ray_type=t.I64, items=[5, 15])
        result = v.within(range_vec)
        assert result.to_python() == [False, True, True, True, False]


class TestFunctionalMixin:
    def test_vector_map_with_operation(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3])
        result = v.map(t.Operation.NEGATE)
        assert result.to_python() == [-1, -2, -3]


class TestSortMixin:
    def test_vector_asc(self):
        v = t.Vector(ray_type=t.I64, items=[3, 1, 4, 1, 5])
        result = v.asc()
        assert result.to_python() == [1, 1, 3, 4, 5]

    def test_vector_desc(self):
        v = t.Vector(ray_type=t.I64, items=[3, 1, 4, 1, 5])
        result = v.desc()
        assert result.to_python() == [5, 4, 3, 1, 1]

    def test_vector_iasc(self):
        v = t.Vector(ray_type=t.I64, items=[3, 1, 4])
        result = v.iasc()
        assert result.to_python() == [1, 0, 2]

    def test_vector_idesc(self):
        v = t.Vector(ray_type=t.I64, items=[3, 1, 4])
        result = v.idesc()
        assert result.to_python() == [2, 0, 1]

    def test_vector_rank(self):
        v = t.Vector(ray_type=t.I64, items=[30, 10, 20])
        result = v.rank()
        assert result.to_python() == [2, 0, 1]

    def test_vector_reverse(self):
        v = t.Vector(ray_type=t.I64, items=[1, 2, 3])
        result = v.reverse()
        assert result.to_python() == [3, 2, 1]

    def test_vector_negate(self):
        v = t.Vector(ray_type=t.I64, items=[1, -2, 3])
        result = v.negate()
        assert result.to_python() == [-1, 2, -3]


class TestMappableMixin:
    def test_dict_key(self):
        d = t.Dict({"a": 1, "b": 2, "c": 3})
        result = d.key()
        assert set(result.to_python()) == {"a", "b", "c"}

    def test_dict_value(self):
        d = t.Dict({"a": 1, "b": 2, "c": 3})
        result = d.value()
        assert set(result.to_python()) == {1, 2, 3}
