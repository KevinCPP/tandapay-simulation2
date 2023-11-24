

def biased_random(lower_bound, upper_bound, center, max_sd=3):
    if not lower_bound <= center <= upper_bound:
        raise ValueError(f"in biased_random: invalid lower_bound={lower_bound}, upper_bound={upper_bound}, and/or center={center}.")
    
    std_dev = max(abs(center - lower_bound), abs(center - upper_bound)) / max_sd

    random_number = np.random.normal(loc=center, scale=std_dev)

    return np.clip(random_number, lower_bound, upper_bound)
