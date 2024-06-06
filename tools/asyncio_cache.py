import asyncio

class AsyncioCache():
    cache_dict:dict[str,asyncio.Future] = {}
    cache_key_list = []
    def __init__(self,max_size=100) -> None:
        self.max_size = max_size

    async def _run(self,future:asyncio.Future, fn):
        future.set_result(fn())

    def add(self,key:str, fn, no_cache=False):
        '''
            用于缓存函数结果，返回一个future，使用相同的key调用多次，如果第一次还未获取结果，之后的调用将不会执行，如果参数 no_cache = True ,将会在5秒后删除缓存，否则将会按照缓存数量限制管理缓存
            因为此函数主要目的是防止一个异步请求执行未完成时调用就取消了并再次调用，造成永远等不到函数结果。
            key: str key
            no_cache: bool 是否不缓存此次调用，如果是，缓存将会在函数结束后等待5秒再删除
            fn: function 函数
        '''
        if key in self.cache_dict:
            return self.cache_dict[key]
        
        self.cache_dict[key] = asyncio.get_running_loop().create_future() 
        
        self.cache_key_list.append(key)
        if self.max_size >0 and len(self.cache_key_list) > self.max_size:
            self.cache_key_list.pop(0)
            
        asyncio.get_running_loop().create_task(self._run(self.cache_dict[key], fn))
        
        if no_cache:
            async def del_cache(f):
                asyncio.sleep(5)
                self.cache_dict.pop(key)
                
            self.cache_dict[key].add_done_callback(del_cache)
        
        return self.cache_dict[key]