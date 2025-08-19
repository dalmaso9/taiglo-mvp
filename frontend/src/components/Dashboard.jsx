import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { MapPin, Star, Search, Filter, Coffee, Utensils, TreePine, Palette, Clock } from 'lucide-react'
import { Form } from '@/components/ui/form'
import { useForm } from "react-hook-form";
import { UploadExcelField } from "@/components/ui/uploadExcelField";

const API_BASE_URL = 'http://localhost:3000/api'

export default function Dashboard() {
  const { user } = useAuth()
  const [experiences, setExperiences] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState(undefined)
  const [sortBy, setSortBy] = useState('created_at')

  // ---- Form de importação (React Hook Form) ----
  //const importForm = useForm({ defaultValues: { excelFile: null } })

  //const onImportSubmit = importForm.handleSubmit(async (values) => {
  //  if (!values.excelFile) {
  //    alert("Selecione um arquivo Excel.");
  //    return;
  //}
  //const fd = new FormData();
  //fd.append("file", values.excelFile);

  //const res = await fetch(`${API_BASE_URL}/experiences/import-xlsx`, {
  //  method: "POST",
  //  headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
  //  body: fd,
  //});

  //if (!res.ok) {
  //  const msg = await res.text();
  //  alert("Falha na importação: " + msg);
  //  return;
  //}

  //alert("Importado com sucesso!");
  //importForm.reset({ excelFile: null });
  //fetchExperiences(); // recarrega a lista
  //});

  useEffect(() => {
    fetchCategories()
    fetchExperiences()
  }, [selectedCategory, sortBy])

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/categories`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` }
      })
      if (response.ok) {
        const data = await response.json()
        // garanta que id é string (Radix Select exige string)
        const cats = (data.categories || []).map((c) => ({
          id: String(c.id),
          name: String(c.name),
        }))
        setCategories(cats)
        // define um valor inicial seguro quando as categorias chegarem
        if (!selectedCategory) setSelectedCategory('all')
      }
    } catch (error) {
      console.error('Erro ao buscar categorias:', error)
    }
  }

  const fetchExperiences = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        page: '1',
        per_page: '20',
        sort_by: sortBy,
        sort_order: 'desc'
      })

      if (selectedCategory && selectedCategory !== 'all') {
        params.append('category_id', selectedCategory)
      }

      if (searchTerm) {
        params.append('search', searchTerm)
      }

      const response = await fetch(`${API_BASE_URL}/experiences?${params}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` }
      })
      if (response.ok) {
        const data = await response.json()
        setExperiences(data.experiences)
      }
    } catch (error) {
      console.error('Erro ao buscar experiências:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    fetchExperiences()
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

  const formatOpeningHours = (hours) => {
    if (!hours || Object.keys(hours).length === 0) return 'Horário não informado'
    const firstKey = Object.keys(hours)[0]
    return `${firstKey}: ${hours[firstKey]}`
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Bem-vindo, {user?.first_name}! 👋
        </h1>
        <p className="text-gray-600">
          Descubra experiências únicas em São Paulo
        </p>
      </div>

      {/* Search and Filters */}
      <Card className="mb-8">
        <CardContent className="pt-6">
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Buscar experiências..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <div className="flex gap-2">
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger className="w-48">
                    <Filter className="h-4 w-4 mr-2" />
                    <SelectValue placeholder="Categoria" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas as categorias</SelectItem>
                    {categories.map((c) => (
                      <SelectItem key={c.id} value={String(c.id)}>
                        {c.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Ordenar por" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="created_at">Mais recentes</SelectItem>
                    <SelectItem value="rating">Melhor avaliados</SelectItem>
                    <SelectItem value="name">Nome A-Z</SelectItem>
                  </SelectContent>
                </Select>

                <Button type="submit">
                  Buscar
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Importar via planilha */}
    {/*<Card className="mb-8">
      <CardHeader>
        <CardTitle>Importar experiências via planilha</CardTitle>
        <CardDescription>
          Envie um arquivo .xlsx/.xls com as experiências para cadastrar no sistema.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...importForm}>
          <form onSubmit={onImportSubmit} className="flex flex-col md:flex-row items-start gap-4">
            <div className="flex-1 min-w-0">
              <UploadExcelField
                name="excelFile"
                label="Planilha Excel"
                description="Formatos aceitos: .xlsx ou .xls"
                accept=".xlsx,.xls"
              />
            </div>
            <Button type="submit">Importar</Button>
          </form>
        </Form>
      </CardContent>
    </Card>*/}


      {/* Quick Actions */}
      {/*<div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card className="hover:shadow-md transition-shadow cursor-pointer">
          <Link to="/map">
            <CardContent className="pt-6">
              <div className="flex items-center space-x-3">
                <div className="bg-blue-100 rounded-full p-3">
                  <MapPin className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold">Explorar no Mapa</h3>
                  <p className="text-sm text-gray-600">Veja experiências próximas</p>
                </div>
              </div>
            </CardContent>
          </Link>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-3">
              <div className="bg-green-100 rounded-full p-3">
                <Star className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold">Gems Escondidas</h3>
                <p className="text-sm text-gray-600">Lugares únicos e especiais</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <Link to="/profile">
            <CardContent className="pt-6">
              <div className="flex items-center space-x-3">
                <div className="bg-purple-100 rounded-full p-3">
                  <Coffee className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold">Minhas Avaliações</h3>
                  <p className="text-sm text-gray-600">Gerencie suas reviews</p>
                </div>
              </div>
            </CardContent>
          </Link>
        </Card>
      </div>*/}

      {/* Experiences Grid */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Experiências em Destaque
        </h2>
        
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <div className="h-48 bg-gray-200 rounded-t-lg"></div>
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
                Tente ajustar os filtros ou fazer uma nova busca
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
                      <div className="h-48 bg-gradient-to-br from-blue-100 to-purple-100 rounded-t-lg flex items-center justify-center">
                        <CategoryIcon className="h-16 w-16 text-gray-400" />
                      </div>
                      {experience.is_hidden_gem && (
                        <Badge className="absolute top-2 right-2 bg-amber-500">
                          💎 Gem
                        </Badge>
                      )}
                    </div>
                    
                    <CardContent className="pt-4">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-semibold text-lg line-clamp-1">
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
                        
                        {experience.opening_hours && (
                          <div className="flex items-center text-sm text-gray-500">
                            <Clock className="h-4 w-4 mr-1" />
                            <span>{formatOpeningHours(experience.opening_hours)}</span>
                          </div>
                        )}
                        
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

      {/* Load More */}
      {experiences.length > 0 && (
        <div className="text-center">
          <Button variant="outline" size="lg">
            Ver mais experiências
          </Button>
        </div>
      )}
    </div>
  )
}

