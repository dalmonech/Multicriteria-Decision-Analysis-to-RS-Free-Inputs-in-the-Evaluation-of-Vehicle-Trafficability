import numpy as np
from osgeo import gdal, gdal_array

# Função para encontrar o valor mais frequente (moda) excluindo sombras
def most_frequent(arr):
    arr = arr[(arr != 7) & (arr >= 0)]  # Exclui sombras (se classe 7) e garante que não há valores negativos
    if len(arr) == 0:
        return 0  # Retorna 0 se todos os vizinhos forem sombras ou a célula estiver isolada
    return np.bincount(arr).argmax()

# Obtém o raster ativo
raster_layer = iface.activeLayer()

if not isinstance(raster_layer, QgsRasterLayer):
    print("A camada ativa não é um raster!")
else:
    print("Raster layer carregado com sucesso!")

    # Pega o caminho do raster ativo
    input_raster_path = raster_layer.dataProvider().dataSourceUri()

    # Abre o raster usando GDAL
    ds = gdal.Open(input_raster_path, gdal.GA_ReadOnly)
    if ds is None:
        print("Erro ao abrir o raster!")
    else:
        print("Raster aberto com sucesso!")

        # Lê a primeira banda do raster
        band = ds.GetRasterBand(1)
        raster_data = band.ReadAsArray()

        rows, cols = raster_data.shape

        # Cria um array numpy para armazenar o raster modificado
        filtered_data = np.copy(raster_data)

        # Limite de iterações
        max_iterations = 100
        iterations = 0

        while True:
            changes_made = False
            iterations += 1

            for i in range(1, rows - 1):
                for j in range(1, cols - 1):
                    if raster_data[i, j] == 7:  # Se a célula é sombra (valor 7)
                        # Extrai os valores dos 8 vizinhos
                        neighbours = raster_data[i - 1:i + 2, j - 1:j + 2].flatten()
                        neighbours = neighbours[neighbours != 7]  # Exclui sombras explicitamente
                        # Substitui pelo valor mais frequente entre os vizinhos
                        new_value = most_frequent(neighbours)
                        if new_value in [1,2,3,4,5,6]:
                            filtered_data[i, j] = new_value
                            changes_made = True
                        else:
                            filtered_data[i,j] = 7
                            changes_made = True
                            

            if not changes_made or iterations >= max_iterations:
                break

            raster_data = np.copy(filtered_data)

        # Define o caminho para salvar o raster filtrado
        output_raster_path = "C:/teste/art_10/sombra.tif"

        # Cria um novo dataset para o raster filtrado
        driver = gdal.GetDriverByName('GTiff')
        out_ds = driver.Create(output_raster_path, cols, rows, 1, gdal.GDT_Byte)
        out_ds.SetGeoTransform(ds.GetGeoTransform())
        out_ds.SetProjection(ds.GetProjection())

        # Escreve os dados filtrados na nova banda
        out_band = out_ds.GetRasterBand(1)
        out_band.WriteArray(filtered_data)
        out_band.SetNoDataValue(0)

        # Fecha os datasets
        out_band.FlushCache()
        out_ds.FlushCache()
        del out_ds

        print("Raster filtrado salvo em:", output_raster_path)
        print("Número de iterações realizadas:", iterations)
