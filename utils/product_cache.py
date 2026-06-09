import json
import os
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv
import redis
import redis.asyncio as redis_async

from models import Product
from schemas import ProductRead
from scraper.generic import handle_amazon_url


load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
PRODUCT_CACHE_TTL_SECONDS = int(os.getenv("PRODUCT_CACHE_TTL_SECONDS", "300"))
PRODUCT_CACHE_PREFIX = "product:url:"

SYNC_REDIS = redis.Redis.from_url(REDIS_URL, decode_responses=True) if REDIS_URL else None
ASYNC_REDIS = redis_async.Redis.from_url(REDIS_URL, decode_responses=True) if REDIS_URL else None


def normalize_product_url(url: str) -> str:
    cleaned_url = url.strip()
    parsed_url = urlparse(cleaned_url)

    if "amazon" in parsed_url.netloc:
        return handle_amazon_url(cleaned_url)

    return cleaned_url


def build_product_cache_key(url: str) -> str:
    return f"{PRODUCT_CACHE_PREFIX}{normalize_product_url(url)}"


def build_product_cache_payload(product: Product, user_count: int | None = None) -> dict[str, Any]:
    product_read = ProductRead(
        id=product.id,
        title=product.title,
        image_url=product.image_url,
        source=product.source,
        url=product.url,
        created_at=product.created_at,
        next_scrape=product.next_scrape,
        price_histories=product.price_histories,
        user_count=user_count if user_count is not None else getattr(product, "user_count", 0),
    )
    return product_read.model_dump(mode="json")


def _decode_cached_product(raw_value: str | None) -> ProductRead | None:
    if not raw_value:
        return None

    return ProductRead.model_validate(json.loads(raw_value))


async def get_cached_product_by_url(url: str) -> ProductRead | None:
    if ASYNC_REDIS is None:
        return None

    cached_value = await ASYNC_REDIS.get(build_product_cache_key(url))
    return _decode_cached_product(cached_value)


async def set_cached_product_by_url(product: Product, user_count: int | None = None) -> None:
    if ASYNC_REDIS is None:
        return

    payload = build_product_cache_payload(product, user_count)
    await ASYNC_REDIS.set(
        build_product_cache_key(product.url),
        json.dumps(payload),
        ex=PRODUCT_CACHE_TTL_SECONDS,
    )


async def delete_cached_product_by_url(url: str) -> None:
    if ASYNC_REDIS is None:
        return

    await ASYNC_REDIS.delete(build_product_cache_key(url))


def get_cached_product_by_url_sync(url: str) -> ProductRead | None:
    if SYNC_REDIS is None:
        return None

    cached_value = SYNC_REDIS.get(build_product_cache_key(url))
    return _decode_cached_product(cached_value)


def set_cached_product_by_url_sync(product: Product, user_count: int | None = None) -> None:
    if SYNC_REDIS is None:
        return

    payload = build_product_cache_payload(product, user_count)
    SYNC_REDIS.set(
        build_product_cache_key(product.url),
        json.dumps(payload),
        ex=PRODUCT_CACHE_TTL_SECONDS,
    )


def delete_cached_product_by_url_sync(url: str) -> None:
    if SYNC_REDIS is None:
        return

    SYNC_REDIS.delete(build_product_cache_key(url))