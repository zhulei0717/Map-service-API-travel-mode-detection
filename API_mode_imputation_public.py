'''
Copyrigt Dr. Lei Zhu
Author: Dr. Lei Zhu
Questions to Email: zhulei0717@gmail.com

'''


import csv
import datetime
import pandas
import numpy as np
import pylab as mp
import operator
import glob

import urllib2
import string
import json
import os

import lcss
from collections import Counter
from pytz import timezone
import calendar

import hmac
import base64
import urlparse
import hashlib


def read_orig(persion_id):
	orig_content = []
	for each in csv.DictReader(open("%s.csv" % persion_id)):
		orig_content += [each]
	return orig_content

def main(persion_id):
	route_time = {}
	pd = pandas.read_csv("StopPointStageCoordsForGIS_%s.txt" % persion_id, delimiter = '\t')
	stageId, coordId, Mode = pd["stageId"], pd["coordId"], pd["Mode"]

	pd_coord = pandas.read_csv("CoordsForAnalysis_%s.txt" % persion_id, delimiter = '\t')
	coordId_all, date, time, lon, lat, distance = pd_coord['CoordID'], pd_coord['Date'], pd_coord['Time'], pd_coord['X'], pd_coord['Y'], pd_coord['Distance']
	
	last_coord_index = list(coordId_all)[-1]
	# print last_coord_index

	route_indicator = mp.mlab.find(np.r_[1, np.diff(stageId) > 0])
	start_coord_Id = []
	end_coord_Id = []

	for each in route_indicator:
		start_coord_Id += [coordId[each]]
		if each-1 > 0:
			end_coord_Id += [coordId[each-1]]
	end_coord_Id += [list(coordId)[-1]]

	stages_list = zip(start_coord_Id, end_coord_Id)
	
	if end_coord_Id[-1] != last_coord_index:
		breakpoints = [-1] + sorted(list(set(start_coord_Id + end_coord_Id))) + [last_coord_index]
	else:
		breakpoints = [-1] + sorted(list(set(start_coord_Id + end_coord_Id)))

	segment = []
	segment_dic = {}
	segment_id = 0
	coord_seq = []

	for i in range(len(breakpoints)-1):
		# stage segments
		if (breakpoints[i], breakpoints[i+1]) in stages_list:
			
			d = list(date)[breakpoints[i]].split('.') 
			t = list(time)[breakpoints[i]].split(':')
			start_dt = datetime.datetime(int(d[2]), int(d[1]), int(d[0]), int(t[0]), int(t[1]), int(t[2]))

			d = list(date)[breakpoints[i+1]].split('.') 
			t = list(time)[breakpoints[i+1]].split(':')
			end_dt = datetime.datetime(int(d[2]), int(d[1]), int(d[0]), int(t[0]), int(t[1]), int(t[2]))

			start_lon = list(lon)[breakpoints[i]]
			start_lat = list(lat)[breakpoints[i]]
			end_lon = list(lon)[breakpoints[i+1]]
			end_lat = list(lat)[breakpoints[i+1]]
			dist = sum(list(distance)[breakpoints[i]: breakpoints[i+1]])

			lon_list = list(lon)[breakpoints[i]: breakpoints[i+1]]
			lat_list = list(lat)[breakpoints[i]: breakpoints[i+1]]
			coord_seq = zip(lat_list, lon_list)

			segment += [(breakpoints[i], breakpoints[i+1])]
			stageId = stages_list.index((breakpoints[i], breakpoints[i+1]))
			segment_dic[(breakpoints[i], breakpoints[i+1])] = [segment_id, stageId, 
				Mode[list(coordId).index(breakpoints[i])], 
				start_dt.strftime('%m/%d/%Y %H:%M:%S'), 
				end_dt.strftime('%m/%d/%Y %H:%M:%S'), 
				(end_dt - start_dt).total_seconds(),
				start_lon, start_lat,
				end_lon, end_lat,
				dist,
				coord_seq,
				]
			segment_id += 1

		## activity segments
		else:
			stageId = None
			mode = "Activity_Others"

			## pass the sequencial segment
			if breakpoints[i+1] == breakpoints[i]+1:
				continue
			# if it is the last segment
			if breakpoints[i+1] != last_coord_index:
				d = list(date)[breakpoints[i]+1].split('.') 
				t = list(time)[breakpoints[i]+1].split(':')
				start_dt = datetime.datetime(int(d[2]), int(d[1]), int(d[0]), int(t[0]), int(t[1]), int(t[2]))

				d = list(date)[breakpoints[i+1]-1].split('.') 
				t = list(time)[breakpoints[i+1]-1].split(':')
				end_dt = datetime.datetime(int(d[2]), int(d[1]), int(d[0]), int(t[0]), int(t[1]), int(t[2]))

				start_lon = list(lon)[breakpoints[i]+1]
				start_lat = list(lat)[breakpoints[i]+1]
				end_lon = list(lon)[breakpoints[i+1]-1]
				end_lat = list(lat)[breakpoints[i+1]-1]
				dist = sum(list(distance)[breakpoints[i]+1: breakpoints[i+1]-1])

				lon_list = list(lon)[breakpoints[i]+1: breakpoints[i+1]-1]
				lat_list = list(lat)[breakpoints[i]+1: breakpoints[i+1]-1]
				coord_seq = zip(lat_list, lon_list)

				segment += [(breakpoints[i]+1, breakpoints[i+1]-1)]
				segment_dic[(breakpoints[i]+1, breakpoints[i+1]-1)] = [segment_id, stageId, 
					mode,
					start_dt.strftime('%m/%d/%Y %H:%M:%S'), 
					end_dt.strftime('%m/%d/%Y %H:%M:%S'), 
					(end_dt - start_dt).total_seconds(),
					start_lon, start_lat,
					end_lon, end_lat,
					dist,
					coord_seq,
					]
				segment_id += 1

			# normal segment process
			else:
				
				d = list(date)[breakpoints[i]+1].split('.') 
				t = list(time)[breakpoints[i]+1].split(':')
				start_dt = datetime.datetime(int(d[2]), int(d[1]), int(d[0]), int(t[0]), int(t[1]), int(t[2]))

				d = list(date)[breakpoints[i+1]].split('.') 
				t = list(time)[breakpoints[i+1]].split(':')
				end_dt = datetime.datetime(int(d[2]), int(d[1]), int(d[0]), int(t[0]), int(t[1]), int(t[2]))

				start_lon = list(lon)[breakpoints[i]+1]
				start_lat = list(lat)[breakpoints[i]+1]
				end_lon = list(lon)[breakpoints[i+1]]
				end_lat = list(lat)[breakpoints[i+1]]
				dist = sum(list(distance)[breakpoints[i]+1: breakpoints[i+1]])

				lon_list = list(lon)[breakpoints[i]+1: breakpoints[i+1]]
				lat_list = list(lat)[breakpoints[i]+1: breakpoints[i+1]]
				coord_seq = zip(lat_list, lon_list)

				segment += [(breakpoints[i]+1, breakpoints[i+1])]
				segment_dic[(breakpoints[i]+1, breakpoints[i+1])] = [segment_id, stageId, 
					mode, 
					start_dt.strftime('%m/%d/%Y %H:%M:%S'), 
					end_dt.strftime('%m/%d/%Y %H:%M:%S'), 
					(end_dt - start_dt).total_seconds(),
					start_lon, start_lat,
					end_lon, end_lat,
					dist,
					coord_seq,
					]

				segment_id += 1

	return segment_dic

def google_directions(origin, destination, mode, departure_timestamp, direction_key):
	url_string = "https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&mode=%s&language=en&units=imperial&key=%s" % (
		origin, destination, mode, direction_key)
	content = urllib2.urlopen(url_string).read()
	cont = json.loads(content)

	g_route = []
	# only one route
	duration_sec = cont['routes'][0]["legs"][0]["duration"]["value"]
	distance_meter = cont['routes'][0]["legs"][0]["distance"]["value"]

	for ele in cont['routes'][0]["legs"][0]["steps"]:
		# print ele
		dist_seg_meter = ele["distance"]["value"]
		duration_seg_sec = ele["duration"]["value"]
		start_coord = ele["start_location"]
		end_coord = ele["end_location"]

		g_route += [(start_coord, end_coord, duration_seg_sec, dist_seg_meter)]
	return duration_sec, distance_meter, g_route

def google_directions_for_traffic_time(origin, destination, mode, departure_timestamp, direction_key, way_points_str = None):
	#### it seem using waypoints will lost the traffic condition travel time information;;
	# if way_points_str != None:
	# 	url_string = "https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&mode=%s&language=en&departure_time=%s&waypoints=%s&units=imperial&key=%s" % (
	# 		origin, destination, mode, departure_timestamp, way_points_str, direction_key)
	# else:
	# 	url_string = "https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&mode=%s&language=en&departure_time=%s&units=imperial&key=%s" % (
	# 		origin, destination, mode, departure_timestamp, direction_key)

	# url_string = "https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&mode=%s&language=en&departure_time=%s&units=imperial&key=%s" % (
	# 		origin, destination, mode, departure_timestamp, direction_key)

	# input_url = 'http://maps.googleapis.com/maps/api/directions/json?origin='+str(o_lat)+','+str(o_lon)+'&destination='+str(d_lat)+','+str(d_lon)+'&alternatives=true&sensor=false&client=gme-nrel'
	input_url = "https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&mode=%s&language=en&departure_time=%s&units=imperial&client=gme-nrel" % (
			origin, destination, mode, departure_timestamp)
	url = urlparse.urlparse(input_url)
	privateKey = '2XHRCandH1udfnZQ4hlydGt_Ojw='
	urlToSign = url.path + "?" + url.query
	decodedKey = base64.urlsafe_b64decode(privateKey)
	signature = hmac.new(decodedKey, urlToSign, hashlib.sha1)
	encodedSignature = base64.urlsafe_b64encode(signature.digest())
	originalUrl = url.scheme + "://" + url.netloc + url.path + "?" + url.query
	Full_URL = originalUrl + "&signature=" + encodedSignature

	# print Full_URL
	try:
		content = urllib2.urlopen(Full_URL).read()
		cont = json.loads(content)
		# print cont
		duration_sec = cont['routes'][0]["legs"][0]["duration_in_traffic"]["value"]
		distance_meter = cont['routes'][0]["legs"][0]["distance"]["value"]
	except:
		print "API request error!"
		return -1, -1
	return duration_sec, distance_meter

def write_segment(segment_dic, persion_id):
	# w = csv.writer(open("%s_summary.csv" % persion_id, 'wb'))
	# w.writerow(["segment_id", "coordId_start", "coordId_end", "stageId", "Mode", "start_time", "end_time", "during"])
	# for key, value in sorted(segment_dic.items(), key=lambda x: x[1]):
	# 	w.writerow([value[0], key[0], key[1], value[1], value[2], value[3], value[4], value[5]])

	segment_ranges = segment_dic.keys()
	segment_value = segment_dic.values()
	a,b = zip(*segment_ranges)
	max_coord =  max(list(set(a+b)))

	mapping_coordid_segmid = {}
	mapping_coordid_mode = {}
	mapping_coordid_stageid = {}
	mapping_coordid_startTime = {}
	mapping_coordid_endTime = {}
	mapping_coordid_duringSec = {}
	for i in range(max(list(set(a+b)))+1):
		for each in segment_ranges:
			if i >= each[0] and i<= each[1]:
				mapping_coordid_segmid[i] = sorted(segment_ranges).index(each)
				mapping_coordid_mode[i] = segment_dic[each][2]
				mapping_coordid_stageid[i] = segment_dic[each][1]
				mapping_coordid_startTime[i] = segment_dic[each][3]
				mapping_coordid_endTime[i] = segment_dic[each][4]
				mapping_coordid_duringSec[i] = segment_dic[each][5]

				break


	content = []
	for each in csv.DictReader(open("CoordsForAnalysis_%s.txt" % persion_id, 'rb'), delimiter = '\t'):
		if int(each["CoordID"]) > max_coord:
			continue
		each.update({"segmetId": mapping_coordid_segmid[int(each["CoordID"])]})
		each.update({"Mode": mapping_coordid_mode[int(each["CoordID"])]})
		each.update({"StageId": mapping_coordid_stageid[int(each["CoordID"])]})
		each.update({"start_time": mapping_coordid_startTime[int(each["CoordID"])]})
		each.update({"end_time": mapping_coordid_endTime[int(each["CoordID"])]})
		each.update({"during": mapping_coordid_duringSec[int(each["CoordID"])]})
		date_string = each["Date"].split('.')
		d = datetime.date(int(date_string[2]), int(date_string[1]), int(date_string[0]))
		date_string = d.strftime("%m-%d-%Y")

		time_string = each["Time"].split(':')
		t = datetime.time(int(time_string[0]), int(time_string[1]), int(time_string[2]))

		time_string = t.strftime("%H:%M:%S")


		each.update({"Date": date_string})
		each.update({"DateTime": date_string+' ' + time_string})

		content +=[each]

	# fieldnames = content[0].keys()
	# cw = csv.DictWriter(open("%s_all_GPS.csv" % persion_id, 'wb'), delimiter = ',', fieldnames =fieldnames)
	# cw.writerow(dict((fn,fn) for fn in fieldnames))
	# for each in content:
	# 	cw.writerow(each)

	coord_all_content = {}
	for each in content:
		coord_all_content.update({each["DateTime"]: each["Mode"]})

	return coord_all_content

def mapbox_api_directions(origin, destination,  mode, departure_timestamp, direction_key):
	url_string = "https://api.mapbox.com/v4/directions/%s/%s;%s.json?alternatives=false&access_token=%s" % (
		mode, origin, destination, direction_key)	
	try:
		content = urllib2.urlopen(url_string).read()
		cont = json.loads(content)
		duration_sec_list = []
		distance_meter_list = []
		g_route_list = []
		# deal ith can't find the routes for OD
		if len(cont['routes']) == 0:
			return -1, -1, -1
		# only one route
		for each in cont['routes']:
			duration_sec_list += [each["duration"]]
			distance_meter_list += [each["distance"]]
			g_route_list += [each["duration"], each["distance"], each["geometry"]["coordinates"]]
		duration_sec = duration_sec_list[0]
		distance_meter = distance_meter_list[0]
	except:
		print "API request error!"
		return -1,-1, []
	return duration_sec, distance_meter, g_route_list

def datetime_convert(dt):
	# dt = datetime.datetime(2012, 05, 21, 10, 23, 56)
	### convert history datetime to future datetime following the same dayofweek and time;
	tz = timezone('US/Pacific')
	utctz = timezone('UTC')
	### set the time zone information
	new_dt = tz.localize(dt)
	# print new_dt
	time = new_dt.time()
	orig_dayofweek = new_dt.weekday()
	#### convert the time zone
	# print new_dt.astimezone(utctz)
	### grab current now
	utc_now = datetime.datetime.utcnow()
	utc_now = utctz.localize(utc_now)
	### convert to work time zone
	now = utc_now.astimezone(tz)
	now_dayofweek = now.weekday()
	if now_dayofweek < orig_dayofweek:
		future = now + datetime.timedelta(days=+(orig_dayofweek-now_dayofweek))
	elif now_dayofweek == orig_dayofweek:
		future = now + datetime.timedelta(days=+7)
	elif now_dayofweek > orig_dayofweek:
		future = now + datetime.timedelta(days=+(7-now_dayofweek + orig_dayofweek))
	future_datetime = datetime.datetime(future.year, future.month, future.day, time.hour, time.minute, time.second)
	future_datetime = tz.localize(future_datetime)
	future_UTC = future_datetime.astimezone(utctz)
	time_tuple_utc = (future.year, future.month, future.day, future_UTC.hour, future_UTC.minute, future_UTC.second)
	timestamp_utc = calendar.timegm(time_tuple_utc)
	return timestamp_utc

def mapbox_filtering_segments(segment_dic, orig_content, persion_id):
	'''
	segment_dic[(breakpoints[i]+1, breakpoints[i+1])] = [segment_id, stageId, 
					mode, 
					start_dt.strftime('%m/%d/%Y %H:%M:%S'), 
					end_dt.strftime('%m/%d/%Y %H:%M:%S'), 
					(end_dt - start_dt).total_seconds(),
					start_lon, start_lat,
					end_lon, end_lat,
					dist,
					coord_seq,
					]
	API_segments[(breakpoints[i]+1, breakpoints[i+1])] = [segment_id, stageId, 
					mode,  ## prev est. mode
					start_dt.strftime('%m/%d/%Y %H:%M:%S'), 
					end_dt.strftime('%m/%d/%Y %H:%M:%S'), 
					(end_dt - start_dt).total_seconds(),
					start_lon, start_lat,
					end_lon, end_lat,
					dist,
					coord_seq,
					content, ### (real tt, real length, real speed, api tt, apt length, api speed,),
					]
	'''
	direction_key = ""
	g_direction_key = ""
	### API results
	API_segments = segment_dic.copy()
	sub_org_seq = []

	traj= []
	path = []
	seq_loc = []
	path_full = []
	sub_seq = []
	reversed_sub_seq = []
	speed_threshold = 20.0
	time_penelty = 1.0

	content = []
	api_confident_level = 0

	for coord_pair, values in sorted(segment_dic.items()):
		content = []
		api_confident_level = 0
		api_est_mode = "Can't estimated by API!"
		sub_seq = orig_content[coord_pair[0]: coord_pair[-1]+1]
		reversed_sub_seq = list(reversed(sub_seq))

		pre_est_mode = str(values[2])
		if  pre_est_mode == 'walk' or pre_est_mode == 'Activity_Others':
			print coord_pair, "walk or Activity_Others, don't process"
			continue
		
		org_index = 0
		dest_index = coord_pair[-1] - coord_pair[0]
		# print coord_pair, pre_est_mode,values[0], values[0]
		origin = sub_seq[0]['lon'] +","+ sub_seq[0]['lat']
		destination = sub_seq[-1]['lon'] + "," + sub_seq[-1]['lat']

		for each in sub_seq:
			if float(each['speed']) < speed_threshold:
				continue
			origin = each['lon'] +","+ each['lat']
			org_index = sub_seq.index(each)
			break

		for each in reversed_sub_seq:
			if float(each['speed']) < speed_threshold:
				continue
			destination = each['lon'] +","+ each['lat']
			dest_index = sub_seq.index(each)
			break

		real_org = sub_seq[org_index]
		real_dest = sub_seq[dest_index]
		# print org_index, real_org
		# print dest_index, real_dest
		real_tt_sec = (datetime.datetime.strptime(real_dest['time'], '%Y-%m-%d %H:%M:%S')- datetime.datetime.strptime(real_org['time'], '%Y-%m-%d %H:%M:%S')).total_seconds()
		real_length_mile = lcss.traj_length(sub_seq[org_index: dest_index+1])

		#### skip the short routes
		if real_length_mile < 0.05:
			print coord_pair, "too short to process!! don't process"
			continue
		real_avg_speed = real_length_mile/(real_tt_sec/3600.0)
		
		#### the API processing start
		mode = "mapbox.driving"
		g_mode = "driving"
		departure_timestamp = int((datetime.datetime.strptime(values[3], '%m/%d/%Y %H:%M:%S')-datetime.datetime(1970, 1, 1)).total_seconds())
		# departure_timestamp = int((datetime.datetime.strptime(values[3], '%Y-%m-%d %H:%M:%S')-datetime.datetime(1970, 1, 1)).total_seconds())
		duration_sec, distance_meter, g_route = mapbox_api_directions(origin, destination, mode, departure_timestamp, direction_key)
		# if can;t find a route for a OD, don't process and continue
		# print coord_pair, g_route
		if duration_sec==0:
			print coord_pair, " too short!!"
			continue
		if duration_sec == -1:
			print coord_pair, " can't find a path!!"
			continue
		api_route = [[index] + g_route[-1][index] for index in range(len(g_route[-1]))]
		sub_org_seq = orig_content[coord_pair[0]: coord_pair[-1]+1]
		sub_org_seq = [[float(ele['lon']), float(ele['lat'])] for ele in sub_org_seq]
		score =  lcss.LCSS_seq(sub_org_seq, api_route)
		sub_seq_loc = [coord_pair[0]+1, coord_pair[0]+1+len(sub_org_seq)-1]
		path_full = [g_route]

		if score < 0.9:		## if less than 0.9, further process starts. 
			### path_full = [each["duration"], each["distance"], each["geometry"]["coordinates"]]
			path_full = process([sub_org_seq], [g_route[-1]], [sub_seq_loc], orig_content, path_full)
		
		dt = datetime.datetime.strptime(real_org['time'], '%Y-%m-%d %H:%M:%S')
		timestamp_utc = datetime_convert(dt)
		# print timestamp_utc

		##### post-process
		api_full_route = []
		way_points = []
		time_sec = 0.0
		time_sec_API = 0.0
		dist_meter = 0.0
		dist_meter_google_API = 0.0

		if len(path_full) > 1:
			for durance, distance, route in path_full:
				g_origin = str(route[0][1]) + "," + str(route[0][0])
				g_destination = str(route[-1][1]) + "," + str(route[-1][0])

				time, length = google_directions_for_traffic_time(g_origin, g_destination, g_mode, timestamp_utc, g_direction_key)
				time_sec_API += float(time)
				time_sec += float(durance)
				dist_meter += float(distance)
				dist_meter_google_API += float(length)
				api_full_route += route

			if time_sec_API == 0.0:
				time_sec_API = -1
			api_avg_speed = dist_meter*0.000621371/(time_sec/3600.0)
			google_api_avg_speed = dist_meter_google_API*0.000621371/(time_sec_API/3600.0)
		else:
			time_sec = path_full[0][0]
			dist_meter = path_full[0][1]
			api_full_route += path_full[0][2]
			api_avg_speed = dist_meter*0.000621371/(time_sec/3600.0)

			g_origin = str(api_full_route[0][1]) + "," + str(api_full_route[0][0])
			g_destination = str(api_full_route[-1][1]) + "," + str(api_full_route[-1][0])
			time_sec_API, dist_meter_google_API = google_directions_for_traffic_time(g_origin, g_destination, g_mode, timestamp_utc, g_direction_key)
			if time_sec_API == 0.0:
				time_sec_API = -1
			google_api_avg_speed = dist_meter_google_API*0.000621371/(time_sec_API/3600.0)

		### deal with API get a extremely high length path;
		if dist_meter*0.000621371/real_length_mile > 2.5:
			print coord_pair, " trip length is wired. can't find a reaonable path!!"
			continue
		
		api_route = [[index] + api_full_route[index] for index in range(len(api_full_route))]
		# print api_route
		sub_org_seq = sub_seq[org_index: dest_index+1]
		# print sub_org_seq
		sub_org_seq = [[float(ele['lon']), float(ele['lat'])] for ele in sub_org_seq]

		score = lcss.LCSS_seq(sub_org_seq, api_route)

		# print coord_pair, values[0], values[1], pre_est_mode, api_est_mode
		print persion_id, coord_pair, " real: ", real_tt_sec, " ", real_length_mile, " ", real_avg_speed, " API: ", time_sec, " ", dist_meter*0.000621371," ",api_avg_speed, " new score: ", score, "google API duration: ", time_sec_API, "google API distance: ", dist_meter_google_API*0.000621371
		content = [real_length_mile, real_avg_speed, dist_meter*0.000621371, api_avg_speed, score, dist_meter_google_API*0.000621371, google_api_avg_speed]
		API_segments[coord_pair].append(content)
	return  API_segments, content

def compare(orig_content, coord_all_content):
	mapping_String2int = {"Activity_Others": -1, 
							"walk": 1,
							"bike": 2,
							"car": 5,
							"urbanPuT": 18,
						}
	dict_int2str = {1: "walk",
					2: "bike",
					5: "car",
					6: "car",
					7: "car",
					18: "urbanPuT"
					}
	comp_content = []
	i = 0
	j = 0
	real_car = 0
	real_bike = 0
	reak_walk = 0
	real_urbanPuT = 0

	est_car = 0
	car_correct_car = 0
	car_correct_bike = 0
	car_corecct_walk = 0
	car_corect_urbanPut = 0

	est_none_car = 0
	none_car_correct_car = 0
	none_car_correct_none_car = 0

	est_bike = 0
	est_walk = 0
	est_urbanPut = 0
	est_others = 0

	segment_id = 0
	pred_tripid = 0
	pred_stageid = 0

	for each in orig_content:
		if each["tripID"] !=  pred_tripid or each["stageID"] != pred_stageid:
			segment_id += 1
		dt =  datetime.datetime.strptime(each["time"], "%Y-%m-%d %H:%M:%S")
		new_dt_string = dt.strftime("%m-%d-%Y %H:%M:%S")
		each.update({"Mode": dict_int2str.get(int(each["Mode"]), -1)})
		each.update({"est_mode": coord_all_content.get(new_dt_string, -3)})
		each.update({"segmentID": segment_id})

		comp_content += [each]

		if each["est_mode"] =='car':
			est_car +=1
			if each["Mode"] =='car':
				car_correct_car += 1
			if each["Mode"] == 'bike':
				car_correct_bike += 1
			if each["Mode"] == 'walk':
				car_corecct_walk += 1
			if each["Mode"] == 'urbanPuT':
				car_corect_urbanPut += 1

		if each["est_mode"] != 'car':
			est_none_car += 1
			if each["Mode"] == 'car':
				none_car_correct_car += 1
			else:
				none_car_correct_none_car += 1

	return comp_content, est_car, car_correct_car, car_correct_bike, car_corecct_walk, car_corect_urbanPut, est_none_car, none_car_correct_car, none_car_correct_none_car

def writer_comp(comp_content, persion_id):
	fieldnames = comp_content[0].keys()
	cw = csv.DictWriter(open("%s_comp_content_g.csv" % persion_id, 'wb'), delimiter = ',', fieldnames =fieldnames)
	cw.writerow(dict((fn,fn) for fn in fieldnames))
	for each in comp_content:
		cw.writerow(each)

def mapbox_segments_path_finding(new_seq_loc, orig_content, traj, path, seq_loc, g_route):
	direction_key = "" ### your mapbox key
	mapbox_segments = {}
	sub_org_seq = []

	old_traj = traj[:]
	old_path = path[:]
	old_seq = seq_loc[:]
	old_g_route = g_route[:]

	trip_durance_threshold = 60 # 5 mins trip
	speed_threshold = 20.0

	traj= []
	path = []
	seq_loc = []
	path_full = []

	for coord_pair in sorted(new_seq_loc):
		if coord_pair in old_seq:
			traj += [old_traj[old_seq.index(coord_pair)]]
			path += [old_path[old_seq.index(coord_pair)]]
			seq_loc += [coord_pair]
			path_full += [old_g_route[old_seq.index(coord_pair)]]
			continue

		sub_seq = orig_content[int(coord_pair[0]): int(coord_pair[-1])+1]
		reverse_sub_seq = list(reversed(sub_seq))

		origin = sub_seq[0]['lon'] +","+ sub_seq[0]['lat']
		for each in sub_seq:
			if float(each['speed']) < speed_threshold:
				continue
			origin = each['lon'] +","+ each['lat']
			break

		destination = sub_seq[-1]['lon'] +","+ sub_seq[-1]['lat']
		for each in reverse_sub_seq:
			if float(each['speed']) < speed_threshold:
				continue
			destination = each['lon'] +","+ each['lat']
			break

		mode = "mapbox.driving"
		# departure_timestamp = int((datetime.datetime.strptime(sub_seq[0]['time'], '%m/%d/%Y %H:%M:%S'   %Y-%m-%d %H:%M:%S )-datetime.datetime(1970, 1, 1)).total_seconds())
		departure_timestamp = int((datetime.datetime.strptime(sub_seq[0]['time'], '%Y-%m-%d %H:%M:%S')-datetime.datetime(1970, 1, 1)).total_seconds())

		duration_sec, distance_meter, g_route = mapbox_api_directions(origin, destination, mode, departure_timestamp, direction_key)
		# if can;t find a route for a OD, don't process and continue
		# print coord_pair, g_route
		api_route = [[index] + g_route[-1][index] for index in range(len(g_route[-1]))]
		sub_org_seq = orig_content[coord_pair[0]: coord_pair[-1]+1]
		sub_org_seq = [[float(ele['lon']), float(ele['lat'])] for ele in sub_org_seq]
		# print sub_org_seq
		# print api_route
		# print coord_pair, "score is: " , lcss.LCSS_seq(sub_org_seq, api_route)

		traj += [sub_org_seq]
		path += [g_route[-1]]
		path_full += [g_route]
		seq_loc += [coord_pair]
	return traj, path, seq_loc, path_full

def process(traj, path, seq_loc, orig_content, path_full):
	i= 0
	while(1):
		# print "Iteration-- ", i
		new_seq_loc, low_score_groups  = lcss.regroup(traj, path, seq_loc)
		# print "low_score_groups", low_score_groups
		if new_seq_loc == seq_loc:
			# print "break due to no further segemntation!"
			break
		if len(low_score_groups) == 0:
			# print "break due to no low scire segments"
			break
		traj, path, seq_loc, path_full = mapbox_segments_path_finding(new_seq_loc, orig_content, traj, path, seq_loc, path_full)
		i +=1

	return path_full

def stats(API_segments, orig_content):
	dict_int2str = {1: "walk",
					2: "bike",
					3: "bike",
					4: "bike",
					5: "car",
					6: "car",
					7: "car",
					8: "car",
					9: "car",
					10: "car",
					11: "car",
					13: "urbanPuT",
					14: "urbanPuT",
					15: "urbanPuT",
					16: "urbanPuT",
					17: "urbanPuT",
					18: "urbanPuT",
					19: "urbanPuT",
					20: "urbanPuT",
					21: "urbanPuT",
					22: "urbanPuT",
					23: "urbanPuT",
					24: "urbanPuT",
					25: "urbanPuT",
					26: "urbanPuT",
					27: "27",
					28: "urbanPuT",
					29: "29",
					}
	stat_ele = {}
	
	for pair, value in API_segments.items():
		real_mode_set = []
		# print pair, value
		pre_mode = value[2]
		content = value[-1]
		if len(content) != 7:
			continue
		for i in range(0, pair[1]-pair[0]+1):
			real_mode_set += [orig_content[pair[0] + i]['Mode']]
		real_mode = dict_int2str[int(Counter(real_mode_set).most_common()[0][0])]
		stat_ele.update({pair: [pre_mode,real_mode, content[0], content[1], content[2], content[3], content[4], content[5], content[6]]})
	return stat_ele


if __name__=="__main__":
	print "hello!"
	personid_accuracy = []
	fout = open("new_pie_chart_enhancement_7.0.dat", 'wb')
	cw = csv.writer(fout, delimiter = ',')
	index = 0

	for files in glob.glob("*.csv"):
		persion_id = files.split('.')[0]
		index += 1
		if os.path.isfile("StopPointStageCoordsForGIS_%s.txt" % persion_id) and os.path.isfile("CoordsForAnalysis_%s.txt" % persion_id):
			orig_content = read_orig(persion_id)
			segment_dic = main(persion_id)
			API_segments, content = mapbox_filtering_segments(segment_dic, orig_content, persion_id)
			stat_ele = stats(API_segments, orig_content)
			
			# process(traj, path, seq_loc,orig_content)
			# google_segments = filtering_segments(segment_dic)
			# segment_dic = adjust_by_google(segment_dic, google_segments)
			# coord_all_content = write_segment(segment_dic, persion_id)
			# comp_content, est_car, car_correct_car, car_correct_bike, car_corecct_walk, car_corect_urbanPut, est_none_car, none_car_correct_car, none_car_correct_none_car = compare(orig_content, coord_all_content)
			# writer_comp(comp_content, persion_id)
			
			for pair, value in stat_ele.items():
				cw.writerow((persion_id, pair, value[0], value[1], value[2], value[3], value[4], value[5], value[6], value[7], value[8]))
				fout.flush()


