import raypy

if __name__ == "__main__":
    raypy.ray_init()

    x = raypy.i64(10)
    y = raypy.i64(20)
    z = raypy.ray_add(x, y)

    raypy.drop_obj(x)
    raypy.drop_obj(y)
    raypy.drop_obj(z)

    raypy.ray_clean()

    print("Done")
