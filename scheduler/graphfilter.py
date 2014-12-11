import graphlab
sf = graphlab.SFrame.read_csv('my_data.csv')
m = graphlab.recommender.create(data)
recs = m.recommend()

