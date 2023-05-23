import fs from "fs";

const data = JSON.parse(fs.readFileSync("./data/sample_data.json", "utf8"));

const calcEuclidianDistance = (positions) => {
  let totalMovement = 0;
  for (let i = 1; i < positions.length; i++) {
    const [posVec] = positions[i];
    const [posVec2] = positions[i - 1];

    const [cX, cY, cZ] = posVec;
    const [pX, pY, pZ] = posVec2;

    const dx = cX - pX;
    const dy = cY - pY;
    const dz = cZ - pZ;

    totalMovement += Math.sqrt(dx * dx + dy * dy + dz * dz);
  }
  return totalMovement;
};

const buildEntityList = (data, key = "id") =>
  data.entities.reduce((acc, entity) => {
    const { id, name, isPlayer, side, type, positions, framesFired } = entity;
    const entityKey = entity[key];

    acc[entityKey] = {
      id,
      name,
      isPlayer: !!isPlayer,
      side,
      type,
      totalMovement: calcEuclidianDistance(positions).toFixed(0),
      shotsFired: framesFired.length,
    };
    return acc;
  }, {});

const parseEvents = (data) =>
  data.events
    .map(([_, eventType, victim, killerInfo, distance]) => {
      const [source] = killerInfo || [];
      if (["hit", "killed"].includes(eventType)) {
        return {
          eventType,
          victim,
          source,
          distance,
        };
      }
    })
    .filter(Boolean);

const buildEventDict = (events) =>
  events.reduce((acc, event) => {
    const { eventType, victim, source, distance } = event;

    acc[source] = acc[source] || {};
    acc[source][eventType] = acc[source][eventType] || [];

    acc[source][eventType].push({
      victim,
      distance,
    });
    return acc;
  }, {});

const mergeEvents = (eventDict, entityDict) => {
  const merged = {
    ai: [],
    player: [],
  };
  for (let i = 0; i < Object.keys(eventDict).length; i++) {
    const key = Object.keys(eventDict)[i];
    const events = eventDict[key];
    const entity = entityDict[key];

    const aiPlayerKey = entity?.isPlayer ? "player" : "ai";

    const entityHits = events?.hit?.length || 0;
    const accuracyCalc =
      entity?.shotsFired > 0
        ? ((entityHits / entity?.shotsFired) * 100).toFixed(0)
        : "0";

    const averageHitDistance =
      events?.hit.reduce((acc, { distance }) => acc + distance, 0) /
      (events?.hit?.length || 1);

    merged[aiPlayerKey].push({
      ...entity,
      totalMovement: parseInt(`${entity?.totalMovement || 0}`),
      shotsFired: parseInt(`${entity?.shotsFired || 0}`),
      hits: parseInt(`${entityHits || 0}`),
      avgHitDistance: parseInt(averageHitDistance.toFixed(0)),
      kills: parseInt(`${events?.killed?.length || 0}`),
      accuracy: parseInt(accuracyCalc || "0"),
      ...events,
    });
  }
  return merged;
};

const entityDictId = buildEntityList(data);
// const entityDictName = buildEntityList(data, "name");

const events = parseEvents(data);
const eventDict = buildEventDict(events);

const mergedEventsDict = mergeEvents(eventDict, entityDictId);

const outputData = {
  stats: mergedEventsDict,
  mission: {
    name: data.missionName,
    author: data.missionAuthor,
    worldName: data.worldName,
    time: new Date(data.times[0].systemTimeUTC).toLocaleString(),
  },
};

fs.writeFileSync("./output/output.json", JSON.stringify(outputData, null, 2));
