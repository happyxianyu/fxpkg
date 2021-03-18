from fxpkg.util.async_pipeline import *

async def foo(n):
    print('Waiting: ', n)
    await asyncio.sleep(n)
    print('Completing: ', n)
    return n

def stage_callback_foo(i, n):
    async def callback(res):
        print(f'stage: {i}; pre_res: {res}; Waiting: {n}')
        await asyncio.sleep(n)
        print(f'stage: {i}; completing: {n}')
        return i,n
    return callback

def test_pipe_run():
    pipe = AsyncPipeline()
    pipe.add_serial_stages(
        [AsyncPipelineStage(workers_num=3, in_callback = stage_callback_foo(i, i/3)) for i in range(5)]
    )
    for i in range(10):
        pipe.get_input_stage().put_data_nw(i)

    for res in pipe.run_b():
        print(f'Final result: {res}')
    pipe.close_b()

def test_pipe_wait_done():
    pipe = AsyncPipeline()
    pipe.add_serial_stages(
        [AsyncPipelineStage(workers_num=3, in_callback = stage_callback_foo(i, i/3)) for i in range(5)]
    )
    for i in range(10):
        pipe.get_input_stage().put_data_nw(i)

    pipe.wait_done_b()

    for res in pipe.get_outputs():
        print(f'Final result: {res}')
    pipe.close_b()