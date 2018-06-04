import csv
from math import sin, cos, sqrt, atan2, radians
import math




def cal_distance(lat_s, lon_s, lat_e, lon_e):
	# approximate radius of earth in km
	R = 6373.0

	lat1 = radians(lat_s)
	lon1 = radians(lon_s)
	lat2 = radians(lat_e)
	lon2 = radians(lon_e)

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))

	distance = R * c
	dist = distance*0.621371
	# print "Result n mile:", dist
	return dist


def traj_length(traj):
	### traj = {["lat": value, "lon": value], ...}
	traj_dist = 0.0
	for i in range(1, len(traj)):
		traj_dist += cal_distance(float(traj[i-1]['lat']), float(traj[i-1]['lon']), float(traj[i]['lat']), float(traj[i]['lon']))
	return traj_dist


def dist(x1,y1, x2,y2, x3,y3): 

	'''
	# x3,y3 is the point
	# distance from a point to a line
	x: lon
	y: lat
	>>> x1 = 1
	>>> y1 = 0
	>>> x2 = 3
	>>> y2 = 0
	>>> x3 = 1
	>>> y3 = 1
	>>> dist(x1,y1, x2,y2, x3,y3) == 1
	True

	>>> x1 = 1
	>>> y1 = 0
	>>> x2 = 3
	>>> y2 = 0
	>>> x3 = 0
	>>> y3 = 1
	>>> dist(x1,y1, x2,y2, x3,y3)
	1.4142135623730951

	>>> x3 = 2
	>>> y3 = 1
	>>> dist(x1,y1, x2,y2, x3,y3)
	1.0

	>>> x3 = 2
	>>> y3 = 2
	>>> dist(x1,y1, x2,y2, x3,y3)
	2.0

	>>> x2 = 1
	>>> x1 = 1
	>>> y2 = 1
	>>> y2 = 1
	>>> x3 = 2
	>>> y3 = 2
	>>> dist(x1,y1, x2,y2, x3,y3)
	1.4142135623730951
	'''
	small_num = 0.00000001
	px = x2-x1
	py = y2-y1

	something = px*px + py*py
	if float(something) == 0.0:
		# print "wrong links geo! Check"
		something = small_num

	u =  ((x3 - x1) * px + (y3 - y1) * py) / float(something)

	if u > 1:
		u = 1
	elif u < 0:
		u = 0

	x = x1 + u * px
	y = y1 + u * py

	dx = x - x3
	dy = y - y3

	# Note: If the actual distance does not matter,
	# if you only want to compare what this function
	# returns to other results of this function, you
	# can just return the squared distance instead
	# (i.e. remove the sqrt) to gain a little performance
	dist = math.sqrt(dx*dx + dy*dy)
	return dist

def read_series(GPS_serie_filename, path_filename):
	traj = []
	path = []
	index = 0
	traj_group = []
	path_group = []
	traj_new_group = []

	seq_loc = []
	count = 0
	count_start = 0
	i =0

	for each in csv.DictReader(open(GPS_serie_filename)):
		traj_new_group += [each]
		if int(each['group_id']) == index:
			traj_group += [[each['lon'], each['lat']]]
		else:
			index += 1
			traj += [traj_group]
			traj_group = []
			traj_group += [[each['lon'], each['lat']]]

			seq_loc += [[count_start, count-1]]
			count_start = count
		count += 1

	if seq_loc[-1][-1] != count:
		seq_loc += [[seq_loc[-1][-1]+1, count-1]]
	# print seq_loc
	# print len(seq_loc)

	# print traj

	## path is a node coord list for the path segment
	index = 0
	for each in csv.DictReader(open(path_filename)):
		if int(each['group_id']) == index:
			if each['coords_begin'].strip(']').strip('[').split(',') not in path_group:
				path_group += [each['coords_begin'].strip(']').strip('[').split(',')]
			if each['coords_end'].strip(']').strip('[').split(',') not in path_group:
				path_group += [each['coords_end'].strip(']').strip('[').split(',')]
		else:
			index += 1
			path += [path_group]
			path_group = []
			path_group += [each['coords_begin'].strip(']').strip('[').split(',')]

	# print path
	# return traj, path

	# #### path_link represents the path by link as [[f_link_lon, f_link_lat], [t_link_lon, t_link_lat]]
	# index = 0
	# path_link = []
	# for each in csv.DictReader(open(path_filename)):
	# 	if int(each['group_id']) == index:
	# 		if (each['coords_begin'].strip(']').strip('[').split(','), each['coords_end'].strip(']').strip('[').split(',')) not in path_group:
	# 			path_group += [(each['coords_begin'].strip(']').strip('[').split(','), each['coords_end'].strip(']').strip('[').split(','))]
	# 	else:
	# 		index += 1
	# 		path_link += [path_group]
	# 		path_group = []
	# 		path_group += [(each['coords_begin'].strip(']').strip('[').split(','), each['coords_end'].strip(']').strip('[').split(','))]

	# print path_link
	return traj, path, seq_loc

def LCSS(X, Y, dist_eps = 0.001):
	### assume the Path is composed by string lines. 
	### Y is the link sequence of the path

	# print X
	# print Y

	m = len(X)
	n = len(Y)
	C = [[0 for i in range(n + 1)] for j in range(m + 1)]

	for i in range(1, m+1):
		for j in range(1, n+1):
			dt = dist(float(Y[j-1][0][0]), float(Y[j-1][0][1]), float(Y[j-1][1][0]), float(Y[j-1][1][1]), float(X[i-1][0]), float(X[i-1][1]))
			if dt < dist_eps:
				simPts = 1- dt/dist_eps
			else:
				simPts = 0
			C[i][j] = max((C[i-1][j-1] + simPts), C[i][j-1], C[i-1][j])

	if float(min(m,n)):
		simi_score = C[m][n]/float(min(m,n))
	else:
		simi_score = 1

	return simi_score

def LCSS_seq(X, Y, dist_eps = 0.001):
	### assume the Path is composed by string lines. 
	### X is the node sequence of GPS trajectory, in order (lon, lat)
	### Y is the node sequence of path, Y = [[id_1, lon_1, lat_1], [id_2, lon_2, lat_2], [...]]
	'''
	>>> X = [[0,0], [1,1],[2,2], [3,3]]
	>>> Y = [[1,0,0], [2, 1, 1], [3,2,2], [4, 3, 3]]
	>>> LCSS_seq(X,Y)
	1.0
	'''
	new_Y = []
	for i in range(1, len(Y)):
		new_Y += [[Y[i-1][1:], Y[i][1:]]]
	Y = new_Y

	m = len(X)
	n = len(Y)
	C = [[0 for i in range(n + 1)] for j in range(m + 1)]

	for i in range(1, m+1):
		for j in range(1, n+1):
			dt = dist(float(Y[j-1][0][0]), float(Y[j-1][0][1]), float(Y[j-1][1][0]), float(Y[j-1][1][1]), float(X[i-1][0]), float(X[i-1][1]))
			if dt < dist_eps:
				simPts = 1- dt/dist_eps
			else:
				simPts = 0
			C[i][j] = max((C[i-1][j-1] + simPts), C[i][j-1], C[i-1][j])

	if float(min(m,n)):
		simi_score = C[m][n]/float(min(m,n))
	# if float(max(m,n)):
		# simi_score = C[m][n]/float(max(m,n))
	else:
		simi_score = 1

	return simi_score

def min_dist(X,Y):
	'''
	return is a list of min distance from the GPS node to the path; the subscribe is GPS point loc
	'''
	m = len(X)
	n = len(Y)
	min_dist_dict = []

	for i in range(1, m+1):
		min_dist_val = 100
		for j in range(1, n+1):
			dt = dist(float(Y[j-1][0][0]), float(Y[j-1][0][1]), float(Y[j-1][1][0]), float(Y[j-1][1][1]), float(X[i-1][0]), float(X[i-1][1]))
			# if dt < dist_eps:
			# 	dt = 0
			if dt < min_dist_val:
				min_dist_val = dt
		min_dist_dict += [min_dist_val]
	return min_dist_dict

def main(traj, path):

	# print traj
	# print path

	LCSSsore = {}
	min_dist_dict = {}

	path_link = []
	p = []
	for each in path:
		p = []
		for i in range(len(each)-1):
			p += [[each[i], each[i+1]]]
		path_link +=[p]

	for index in range(len(traj)):
		LCSSsore[index] = LCSS(traj[index], path_link[index])
		min_dist_dict[index] = min_dist(traj[index], path_link[index])

	return LCSSsore, min_dist_dict

	# ### try the distance 
	# index  = 8
	# dist_eps = 0.0005
	# min_dist = []
	# for index in range(len(traj)):
	# 	X = traj[index]
	# 	Y = path_link[index]
	# 	m = len(X)
	# 	n = len(Y)
	# 	C = [[0 for i in range(n + 1)] for j in range(m + 1)]
	# 	# print m,n
	# 	min_dist = []
	# 	for i in range(1, m+1):
	# 		min_dist_val = 100
	# 		for j in range(1, n+1):
	# 			dt = dist(float(Y[j-1][0][0]), float(Y[j-1][0][1]), float(Y[j-1][1][0]), float(Y[j-1][1][1]), float(X[i-1][0]), float(X[i-1][1]))
	# 			if dt < dist_eps:
	# 				dt = 0
	# 			if dt < min_dist_val:
	# 				min_dist_val = dt
	# 		min_dist += [min_dist_val]
	# 	if sum(min_dist) != 0:
	# 		valid_list = [i for i in min_dist if i > 0]
	# 		avg_dist = sum(valid_list)/len(valid_list)
	# 	else:
	# 		avg_dist = 0
	# 	max_dist_val = max(min_dist)
	# 	print index, avg_dist, max_dist_val, min_dist

def group_process(LCSSsore, min_dist_dict, traj, seq_loc, sim_threhold = 0.9):
	'''
	process the group segment by LCSS score and seperate the low score segment;
	'''

	new_seq_loc = seq_loc[:]
	candidate_groups = {}
	candidate_groups_id_list = []

	low_score_groups = []

	for group_id, score in LCSSsore.items():
		if score > sim_threhold:
			continue
		candidate_groups[group_id] = score

	candidate_groups_id_list = sorted(candidate_groups, key=candidate_groups.get)
	# print candidate_groups
	# print candidate_groups_id_list

	for each in candidate_groups_id_list:
		# print each
		start_loc, end_loc = seq_loc[each]
		low_score_groups += [[start_loc, end_loc, candidate_groups[each]]]
		segment_loc_seg = traj_segment(min_dist_dict[each], start_loc)
	
		if segment_loc_seg != []:
			# print each, segment_loc_seg
			new_seq_loc.remove(seq_loc[each])
			for ele in segment_loc_seg:
				new_seq_loc.append(ele)

	return sorted(new_seq_loc), sorted(low_score_groups)

def traj_segment(min_dist, start_loc):
	'''
	separate the unsimilar traj into several small pieces
	consider the max min distance to the link and the edge points of close segment to determine the sub-group to process
	'''
	# relative segmental location points list
	rel_segment_loc = []
	dist_eps = 0.001
	min_seg_interval = 5

	# print min_dist
	# print len(min_dist)
	last_loc = len(min_dist) - 1

	max_min_dist_loc = min_dist.index(max(min_dist))
	rel_segment_loc += [max_min_dist_loc]

	for i in range(1, len(min_dist)-1):
		if min_dist[i] <= dist_eps and min_dist[i-1] > dist_eps or min_dist[i] <= dist_eps and min_dist[i+1] > dist_eps:
			rel_segment_loc += [i]

	rel_segment_loc = sorted(rel_segment_loc)
	if 0 not in rel_segment_loc:
		if rel_segment_loc[0] > min_seg_interval:
			rel_segment_loc += [0]
		else:
			rel_segment_loc[0] = 0


	if last_loc not in rel_segment_loc:
		if (last_loc - max(rel_segment_loc)) > min_seg_interval:
			rel_segment_loc += [last_loc]
		else:
			rel_segment_loc = sorted(rel_segment_loc)
			rel_segment_loc[-1] = last_loc


	rel_segment_loc = sorted(rel_segment_loc)
	segment_loc_seg = []
	# print rel_segment_loc
	for i in range(len(rel_segment_loc)-1):
		if i == len(rel_segment_loc)-2 :
			segment_loc_seg += [[rel_segment_loc[i] + start_loc, rel_segment_loc[i+1] + start_loc]]
		elif rel_segment_loc[i+1]-1 - rel_segment_loc[i] > 0:
			segment_loc_seg += [[rel_segment_loc[i] + start_loc, rel_segment_loc[i+1]-1 + start_loc]]

	if len(segment_loc_seg)  == 1:
		return []
	else:
		return segment_loc_seg

def regroup(traj, path, seq_loc):
	#### traj is the coord list of GPS points,
	#### path is a coord list of path nodes (lon, lat),...
	LCSSsore, min_dist_dict = main(traj, path)
	average_score = sum(LCSSsore.values())/len(LCSSsore)
	# print "average_score: ", average_score

	### stop criterion: all segment similar scores are greater and equals to (>=) a value 0.9 similarity score 
	# print LCSSsore
	## process each groups by scores and min_distance features 
	new_seq_loc, low_score_groups = group_process(LCSSsore, min_dist_dict, traj, seq_loc)

	# print low_score_groups

	return sorted(new_seq_loc), low_score_groups


if __name__=="__main__":

	import doctest
	doctest.testmod()

	GPS_serie_filename = "721130803_new.csv"
	path_filename = "seg_link_seq.csv"
	traj, path, seq_loc = read_series(GPS_serie_filename, path_filename)
	#### traj is a grouped lon/lat coord list;  
	#### path is a list of coord of graphical path nodes;
	#### seq_loc is the old group location list

	new_seq_loc, low_score_groups = regroup(traj, path, seq_loc)

	print new_seq_loc





	