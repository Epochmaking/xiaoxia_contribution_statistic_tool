# pylint: disable=unnecessary-pass

class AnalyseThreadError(RuntimeError):
    """
    分析线程异常类
    """
    pass

class GetArticleContentError(RuntimeError):
    """
    获取文章内容线程异常类
    """
    pass

# pylint: enable=unnecessary-pass

__all__ = [
    "AnalyseThreadError",
    "GetArticleContentError",
]