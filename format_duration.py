def format_duration(seconds: int):
    days, seconds = divmod(seconds, 86400)  # 86400 = 60 * 60 * 24
    hours, seconds = divmod(seconds, 3600)  # 3600 = 60 * 60
    minutes, seconds = divmod(seconds, 60)
    d, h, m, s = int(days), int(hours), int(minutes), int(seconds)
    return f"{'' if d == 0 else f'{d}d '}{'' if h == 0 else f'{h}h '}{'' if m == 0 else f'{m}m '}{s}s"
