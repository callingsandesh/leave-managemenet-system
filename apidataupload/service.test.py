import datetime
from service import generate_date_intervals
def test_generate_date_intervals_multiple_intervals():
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 12, 31)
    intervals = generate_date_intervals(start_date, end_date)
    
    assert len(intervals) > 1
    assert intervals[0][0] == start_date
    assert intervals[-1][1] == end_date
    
    for interval in intervals:
        assert interval[0] <= interval[1]
        assert (interval[1] - interval[0]).days <= 180
    
    for i in range(len(intervals) - 1):
        assert (intervals[i+1][0] - intervals[i][1]).days == 1