from src.decorator import controller, get

@controller('/log')
class LogController:

    @get('/')
    def test(self):
        return {'test': 'hello'}
    
    @get('/test')
    async def test_log(self):
        return 'asd'