// mongosh: load('mongodb_queries.js'), após mongodb_schema.js.
const geoDB = db.getSiblingDB('academy');
print('Vizinhos em até 1000 metros:');
printjson(geoDB.pontos.aggregate([
 {$geoNear:{near:{type:'Point',coordinates:[-48.55,-27.59]},
   key:'localizacao', distanceField:'distancia_m', maxDistance:1000, spherical:true}},
 {$project:{nome:1,categoria:1,distancia_m:1}}
]).toArray());
// Anel exterior FECHADO; coordenadas longitude/latitude. Sem CRS personalizado.
print('Pontos dentro do polígono:');
printjson(geoDB.pontos.find({localizacao:{$geoWithin:{$geometry:{type:'Polygon',coordinates:[[
 [-48.56,-27.60],[-48.53,-27.60],[-48.53,-27.58],[-48.56,-27.58],[-48.56,-27.60]
]]}}}}).toArray());
print('Contagem por categoria:');
printjson(geoDB.pontos.aggregate([{$group:{_id:'$categoria',total:{$sum:1}}},{$sort:{total:-1,_id:1}}]).toArray());
