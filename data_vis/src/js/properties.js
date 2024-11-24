import props from './properties.json' with { type: "json"};

const properties = {
    Age: props.Age,
    Height: props.Height,
    Weight: props.Weight,
    Team: props.Team,
    NOC: props.NOC,
    Games: props.Games,
    Year: props.Year,
    City: props.City,
    Sport: props.Sport,
    Event: props.Event,
    Medal: props.Medal,
    BMI: props.BMI,
    GDP: props.GDP
}

properties.Properties = Object.keys(properties);

export default properties;