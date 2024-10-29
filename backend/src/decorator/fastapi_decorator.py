from fastapi import APIRouter


def controller(prefix: str):
    def decorator(cls):
        instance = cls()
        router = APIRouter(prefix=prefix, tags=[cls.__name__.replace('Controller', '')])

        # 인스턴스의 method들에 접근하여 route_info가 있는지 확인
        for attr_name in dir(instance):
            attr = getattr(instance, attr_name)
            if callable(attr) and hasattr(attr, 'route_info'):
                method, path = attr.route_info
                # 여기서 method를 인스턴스의 method로 추가
                router.add_api_route(path, attr, methods=[method])

        # 클래스에 router 속성을 추가하여 외부에서 접근 가능하게 함
        cls.router = router
        return cls

    return decorator

def get(path: str):
    def decorator(func):
        func.route_info = ("GET", path)
        return func

    return decorator

def post(path: str):
    def decorator(func):
        func.route_info = ("POST", path)
        return func

    return decorator

def put(path: str):
    def decorator(func):
        func.route_info = ("PUT", path)
        return func

    return decorator

def delete(path: str):
    def decorator(func):
        func.route_info = ("DELETE", path)
        return func

    return decorator
