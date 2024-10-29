from src.decorator import controller, get


# 참고용 controller 
@controller('/log')
class LogController:

    @get('/')
    def test(self):
        return {'test': 'hello'}
    
    @get('/test')
    async def test_log(self):
        return 'asd'
    
    @get('/view/{view_id}')
    async def view_test(self, view_id):
        return {
            'view_id': view_id,
            'test': 1234
        }