const Typesense = require('typesense');
const _ = require('lodash');
module.exports = (async () => {
  const client = new Typesense.Client({
    nodes: [
      {
        host: 'localhost',
        port: '8108',
        protocol: 'http',
      },
    ],
    apiKey: 'xyz',
  });
  const schema = process.argv.slice(2)[0];
  const collections = await client.collections().retrieve();
  const collectionNames = collections.map(collection => {
    return collection.name;
  });
  console.log(collectionNames);
  try {
    if (_.includes(collectionNames, schema) === true) {
      await client.collections(schema).delete();
      console.log(`Collection ${schema} deleted successfully`);
    } else {
      console.log(`Collection ${schema} not present`);
    }
  } catch (error) {
    console.error(error);
  }
})();
