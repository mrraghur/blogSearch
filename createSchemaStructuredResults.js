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

  const schema = {
    name: 'structuredResults',
    fields: [
      { name: 'text', type: 'string' },
      { name: 'url', type: 'string' },
    ],
  };
  const collections = await client.collections().retrieve();
  const collectionNames = collections.map(collection => {
    return collection.name;
  });
  console.log(collectionNames);
  try {
    if (_.includes(collectionNames, schema.name) === false) {
      await client.collections().create(schema);
      console.log(`Collection ${schema.name} created successfully`);
    } else {
      console.log(`Collection ${schema.name} already present`);
    }
  } catch (error) {
    console.error(error);
  }
})();
