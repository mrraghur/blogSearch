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
    name: 'blogs',
    fields: [
      { name: 'title', type: 'string' },
      { name: 'text', type: 'string' },
      { name: 'category', type: 'string', facet: true },
      { name: 'url', type: 'string' },
      { name: 'description', type: 'string' },
      { name: 'imgs', type: 'string' },
    ],
  };
  var exportedDocs = await client.collections('blogs').documents().export()
  console.log(exportedDocs)
})();
