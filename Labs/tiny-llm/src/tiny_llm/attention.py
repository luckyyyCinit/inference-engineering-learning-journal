import mlx.core as mx
from .basics import softmax, linear

# Q shape ?
# K shape ?
# K 转置之后 ?
# Q @ K^T 得到 ?
# 为什么除以 sqrt(D) ?
# mask 在哪里加？
# softmax 对哪个 dimension？
# 最后为什么再 @ V？
# MLX 里怎么只 transpose 最后两个维度

    # """
    # A simple implementation of scaled dot product attention. Assuming Q, K, V are of the same shape.
    # Assuming mask is always a float array that you can add to the scores.
    # """
    # factor = mx.rsqrt(query.shape[-1]) if scale is None else scale
    # scores = mx.matmul(query, key.swapaxes(-2, -1)) * factor
    # if mask is not None:
    #     scores = scores + mask
    # return mx.matmul(softmax(scores, axis=-1), value)

def scaled_dot_product_attention_simple(
    query: mx.array,
    key: mx.array,
    value: mx.array,
    scale: float | None = None,
    mask: mx.array | None = None,
) -> mx.array:
    # 1. transpose the last two dimensions
    key_t = key.swapaxes(-2, -1)

    # 2. matrix multiplication:
    # batch-compute all Q_i · K_j dot products
    scores = query @ key_t

    # 3. scale
    factor = mx.rsqrt(query.shape[-1]) if scale is None else scale
    scores = scores * factor

    # 4. mask
    if mask is not None:
        scores = scores + mask

    # 5. softmax -> attention weights
    weights = mx.softmax(scores, axis=-1)

    # 6. weighted sum of values
    output = weights @ value

    return output

class SimpleMultiHeadAttention:
    def __init__(
        self,
        hidden_size: int,
        num_heads: int,
        wq: mx.array,
        wk: mx.array,
        wv: mx.array,
        wo: mx.array,
    ):
        pass

    def __call__(
        self,
        query: mx.array,
        key: mx.array,
        value: mx.array,
        mask: mx.array | None = None,
    ) -> mx.array:
        pass


def causal_mask(L: int, S: int, dtype: mx.Dtype) -> mx.array:
    pass


def scaled_dot_product_attention_grouped(
    query: mx.array,
    key: mx.array,
    value: mx.array,
    scale: float | None = None,
    mask: mx.array | str | None = None,
) -> mx.array:
    pass


def paged_attention(
    query: mx.array,
    key_pages: mx.array,
    value_pages: mx.array,
    block_table: mx.array,
    context_lens: mx.array,
    page_size: int,
    scale: float | None = None,
    mask: mx.array | str | None = None,
) -> mx.array:
    """Attend to paged K/V storage without reconstructing a dense cache.

    Week 3 Day 4 owns the correctness-first decode and long-prefill paths for
    both float32 and BF16. Day 5 optimizes the same public boundary.
    """
    pass
