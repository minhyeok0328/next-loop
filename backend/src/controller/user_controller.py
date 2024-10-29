from src.decorator import controller, get


# 참고용 controller 
@controller('/user')
class UserController:

    @get('/find_user/{user_id}')
    async def find_user(self, user_id: int):
        print('asd')
        return {
            'user_id': user_id
        }
