def count_string_length(text):
    """
    计算字符串长度，包括空格
    Args:
        text: 要计算长度的字符串
    Returns:
        字符串的总长度（包括空格）
    """
    return len(text)

if __name__ == "__main__":
    print(count_string_length("联 系 人：                                                        "))
