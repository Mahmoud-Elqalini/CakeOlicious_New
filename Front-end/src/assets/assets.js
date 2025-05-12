// Shahd Elwan
const imageModules = import.meta.glob('./images/*.{png,jpg,jpeg,svg}', {
  eager: true,
  import: 'default',
});

const images = Object.fromEntries(
  Object.entries(imageModules).map(([path, module]) => {
    const key = path.match(/\.\/images\/(.+)\.(png|jpg|jpeg|svg)$/)?.[1];
    return [key, module];
  })
);

export const getImage = (name) => {
  if (!images[name]) {
    console.warn(`Image "${name}" not found. Available images: ${Object.keys(images).join(', ')}`);
    return null;
  }
  return images[name];
};

export default images;
