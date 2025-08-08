import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { MapPin, Star, Search, Navigation, Coffee, Utensils, TreePine, Palette, Loader2 } from 'lucide-react'

const API_BASE_URL = 'http://localhost:3000/api'

// Coordenadas padrão para São Paulo
const DEFAULT_LOCATION = {
  latitude: -23.5505,
  longitude: -46.6333
}

export default function ExperienceMap() {
  const [experiences, setExperiences] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [userLocation, setUserLocation] = useState(null)
  const [selectedCategory, setSelectedCategory] = useState('')
  const [radiusKm, setRadiusKm] = useState('5')
  const [searchLocation, setSearchLocation] = useState('')

  useEffect(() => {
    fetchCategories()
    getCurrentLocation()
  }, [])

  useEffect(() => {
    if (userLocation) {
      fetchNearbyExperiences()
    }
  }, [userLocation, selectedCategory, radiusKm])

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/categories`)
      if (response.ok) {
        const data = await response.json()
        setCategories(data.categories)
      }
    } catch (error) {
      console.error('Erro ao buscar categorias:', error)
    }
  }

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          })
        },
        (error) => {
          console.log('Erro ao obter localização:', error)
          // Usar localização padrão de São Paulo
          setUserLocation(DEFAULT_LOCATION)
        }
      )
    } else {
      // Usar localização padrão se geolocalização não for suportada
      setUserLocation(DEFAULT_LOCATION)
    }
  }

  const fetchNearbyExperiences = async () => {
    if (!userLocation) return

    try {
      setLoading(true)
      const params = new URLSearchParams({
        latitude: userLocation.latitude.toString(),
        longitude: userLocation.longitude.toString(),
        radius_km: radiusKm,
        limit: '50'
      })

      if (selectedCategory) {
        params.append('category_id', selectedCategory)
      }

      const response = await fetch(`${API_BASE_URL}/experiences/nearby?${params}`)
      if (response.ok) {
        const data = await response.json()
        setExperiences(data.experiences)
      }
    } catch (error) {
      console.error('Erro ao buscar experiências próximas:', error)
    } finally {
      setLoading(false)
    }
  }

  const getCategoryIcon = (categoryName) => {
    const icons = {
      'Cafés': Coffee,
      'Restaurantes': Utensils,
      'Parques': TreePine,
      'Arte': Palette,
      'Museus': Palette
    }
    return icons[categoryName] || MapPin
  }

  const handleLocationSearch = (e) => {
    e.preventDefault()
    // Para o MVP, vamos usar coordenadas fixas baseadas em locais conhecidos de SP
    const locations = {
      'vila madalena': { latitude: -23.5618, longitude: -46.6918 },
      'pinheiros': { latitude: -23.5634, longitude: -46.6823 },
      'jardins': { latitude: -23.5678, longitude: -46.6701 },
      'centro': { latitude: -23.5456, longitude: -46.6389 },
      'ibirapuera': { latitude: -23.5873, longitude: -46.6575 }
    }

    const searchLower = searchLocation.toLowerCase()
    const foundLocation = Object.keys(locations).find(key => 
      searchLower.includes(key) || key.includes(searchLower)
    )

    if (foundLocation) {
      setUserLocation(locations[foundLocation])
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Mapa de Experiências 🗺️
        </h1>
        <p className="text-gray-600">
          Descubra lugares incríveis próximos a você
        </p>
      </div>

      {/* Controls */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Navigation className="h-5 w-5" />
            <span>Busca por Localização</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Location Search */}
          <form onSubmit={handleLocationSearch} className="flex gap-2">
            <Input
              placeholder="Ex: Vila Madalena, Pinheiros, Centro..."
              value={searchLocation}
              onChange={(e) => setSearchLocation(e.target.value)}
              className="flex-1"
            />
            <Button type="submit">
              <Search className="h-4 w-4 mr-2" />
              Buscar
            </Button>
          </form>

          {/* Filters */}
          <div className="flex flex-col md:flex-row gap-4">
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="Categoria" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todas as categorias</SelectItem>
                {categories.map((category) => (
                  <SelectItem key={category.id} value={category.id}>
                    {category.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={radiusKm} onValueChange={setRadiusKm}>
              <SelectTrigger className="w-full md:w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">1 km</SelectItem>
                <SelectItem value="2">2 km</SelectItem>
                <SelectItem value="5">5 km</SelectItem>
                <SelectItem value="10">10 km</SelectItem>
                <SelectItem value="20">20 km</SelectItem>
              </SelectContent>
            </Select>

            <Button onClick={getCurrentLocation} variant="outline">
              <Navigation className="h-4 w-4 mr-2" />
              Minha localização
            </Button>
          </div>

          {/* Current Location Display */}
          {userLocation && (
            <div className="text-sm text-gray-600">
              📍 Buscando em um raio de {radiusKm}km de: {userLocation.latitude.toFixed(4)}, {userLocation.longitude.toFixed(4)}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Map Placeholder */}
      <Card className="mb-8">
        <CardContent className="pt-6">
          <div className="h-96 bg-gradient-to-br from-blue-50 to-green-50 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300">
            <div className="text-center">
              <MapPin className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-700 mb-2">
                Mapa Interativo
              </h3>
              <p className="text-gray-500 max-w-md">
                Em breve: mapa interativo com Mapbox/Leaflet mostrando todas as experiências próximas com marcadores clicáveis
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">
            Experiências Próximas
          </h2>
          {loading && (
            <div className="flex items-center space-x-2 text-gray-600">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Buscando...</span>
            </div>
          )}
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <div className="h-32 bg-gray-200 rounded-t-lg"></div>
                <CardContent className="pt-4">
                  <div className="h-4 bg-gray-200 rounded mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded mb-4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : experiences.length === 0 ? (
          <Card>
            <CardContent className="pt-6 text-center">
              <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Nenhuma experiência encontrada
              </h3>
              <p className="text-gray-600">
                Tente aumentar o raio de busca ou alterar os filtros
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {experiences.map((experience) => {
              const CategoryIcon = getCategoryIcon(experience.category?.name)
              return (
                <Card key={experience.id} className="hover:shadow-lg transition-shadow">
                  <Link to={`/experience/${experience.id}`}>
                    <div className="relative">
                      <div className="h-32 bg-gradient-to-br from-blue-100 to-purple-100 rounded-t-lg flex items-center justify-center">
                        <CategoryIcon className="h-12 w-12 text-gray-400" />
                      </div>
                      {experience.is_hidden_gem && (
                        <Badge className="absolute top-2 right-2 bg-amber-500">
                          💎 Gem
                        </Badge>
                      )}
                      {experience.distance_km !== undefined && (
                        <Badge className="absolute top-2 left-2 bg-blue-500">
                          {experience.distance_km.toFixed(1)}km
                        </Badge>
                      )}
                    </div>
                    
                    <CardContent className="pt-4">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-semibold line-clamp-1">
                          {experience.name}
                        </h3>
                        {experience.average_rating > 0 && (
                          <div className="flex items-center space-x-1">
                            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                            <span className="text-sm font-medium">
                              {experience.average_rating.toFixed(1)}
                            </span>
                          </div>
                        )}
                      </div>
                      
                      <p className="text-gray-600 text-sm line-clamp-2 mb-3">
                        {experience.description}
                      </p>
                      
                      <div className="space-y-2">
                        <div className="flex items-center text-sm text-gray-500">
                          <MapPin className="h-4 w-4 mr-1" />
                          <span className="line-clamp-1">{experience.address}</span>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          {experience.category && (
                            <Badge variant="secondary">
                              {experience.category.name}
                            </Badge>
                          )}
                          
                          {experience.price_range && (
                            <span className="text-sm text-gray-500">
                              {'$'.repeat(experience.price_range)}
                            </span>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Link>
                </Card>
              )
            })}
          </div>
        )}
      </div>

      {/* Info Card */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex items-start space-x-3">
            <MapPin className="h-6 w-6 text-blue-600 mt-1" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">
                Como funciona a busca por proximidade
              </h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Use sua localização atual ou busque por bairros específicos</li>
                <li>• Ajuste o raio de busca de 1km até 20km</li>
                <li>• Filtre por categoria para encontrar exatamente o que procura</li>
                <li>• As distâncias são calculadas em linha reta</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

