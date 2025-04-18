from rayforce import *

if __name__ == "__main__":
    ray_init()
    
    x = i64(10)
    y = i64(20)
    z = ray_add(x, y)

    drop_obj(x)
    drop_obj(y)
    drop_obj(z)

    ray_clean()

    print("Done")