// DataGeo Academy. Execute com mongosh autenticado: load('mongodb_schema.js').
// Banco de laboratório, GeoJSON WGS84: ordem [longitude, latitude].
const academy = db.getSiblingDB('academy');
if (!academy.getCollectionNames().includes('pontos')) {
  academy.createCollection('pontos', {validator: {$jsonSchema: {
    bsonType:'object', required:['nome','categoria','localizacao'], properties:{
      nome:{bsonType:'string', minLength:1}, categoria:{bsonType:'string'},
      localizacao:{bsonType:'object', required:['type','coordinates'], properties:{
        type:{enum:['Point']}, coordinates:{bsonType:'array', minItems:2, maxItems:2,
          items:{bsonType:['double','int','long','decimal']}}
      }}
    }
  }}, validationLevel:'strict', validationAction:'error'});
}
academy.pontos.createIndex({localizacao:'2dsphere'}, {name:'localizacao_2dsphere'});
const exemplos = [
 {_id:'DG_DEMO01',nome:'Escola didática',categoria:'escola',localizacao:{type:'Point',coordinates:[-48.55,-27.59]}},
 {_id:'DG_DEMO02',nome:'Parque didático',categoria:'parque',localizacao:{type:'Point',coordinates:[-48.54,-27.585]}}
];
for (const exemplo of exemplos) {
  academy.pontos.updateOne({_id:exemplo._id}, {$setOnInsert:exemplo}, {upsert:true});
}
print('Dados sintéticos preservados. Índice:');
printjson(academy.pontos.getIndexes());
