import axios from "axios";

export async function apiCall(parameters, endpoint) {
  const response = await axios.get(endpoint, {
    params: parameters,
    paramsSerializer: {
      serialize: (params) => {
        return Object.keys(params)
          .map((key) =>
            Array.isArray(params[key])
              ? params[key]
                  .map((val) => `${key}=${encodeURIComponent(val)}`)
                  .join("&")
              : `${key}=${encodeURIComponent(params[key])}`
          )
          .join("&");
      },
    },
  });
  return response.data;
}

export function allKeys(data) {
  return data.reduce((acc, d) => {
      Object.keys(d.lines).forEach((key) => {
          if (!acc[key]) {
              acc[key] = true;
          }
      });
      return acc;
  },{});
}

export function encodeColor() {
  function* colors() {
    const colors = [
      "red",
      "blue",
      "green",
      "yellow",
      "orange",
      "purple",
      "black",
      "pink",
      "brown",
      "grey",
    ];

    while (colors.length > 0) {
      yield colors.shift();

      if (colors.length === 0) {
        yield "#" + (((1 << 24) * Math.random()) | 0).toString(16);
      }
    }
  }
  const colorGenerator = colors();

  return () => colorGenerator.next().value;
}


export function generateRandomColors(data){
  const colorGenerator = encodeColor();
  const colors = {};
  Object.keys(allKeys(data)).forEach((key) => {
    colors[key] = colorGenerator();
  });
  return colors;
}