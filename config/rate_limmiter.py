from fastapi import Request, HTTPException, status


from config.redis import redis_client


def rate_limiter(limit: int, window: int):

    async def limiter(request: Request):

        client_ip = request.client.host
        path = request.url.path

        key = f"rate_limit:{client_ip}:{path}"

        current_count = await redis_client.incr(key)

        if current_count == 1:
            await redis_client.expire(key, window)

        if current_count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )

    return limiter